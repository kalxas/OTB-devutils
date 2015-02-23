#!/usr/bin/python
#coding=utf8

import sys
import string
import os
import os.path as op
import codeParser
import manifestParser
import createTestManifest
import re
import shutil
from subprocess import call, PIPE
import dispatchTests

def showHelp():
  print "Script to move a source file from an OTB tree (after modularization)"+\
    ". Allows to move source files from a module to an other and operate the "+\
    "corresponding modifications in the build system."
  print "Usage : moveSource.py  OTB_SRC_DIRECTORY  TARGET_MODULE  SOURCES_FILES"
  print "  OTB_SRC_DIRECTORY : checkout of modular OTB (will be modified)"
  print "  TARGET_MODULE     : destination module"
  print "                      use 'group/module' in case of a new module"
  print "  SOURCES_FILES     : list of source files"

def parseModuleDefinition(path):
  depList = {}
  optDepList = {}
  testDepList = {}
  isInModDef = False
  lineBuffer = ""
  lineList = []
  keywords = ["DEPENDS", "OPTIONAL_DEPENDS", "TEST_DEPENDS","EXAMPLE_DEPENDS","DESCRIPTION"]
  
  fd = open(path,'rb')
  for line in fd:
    cleanLine = (line.replace("\t"," ")).strip(" \n\r")
    
    # skip commented line
    idx=cleanLine.find('#')
    if idx != -1:
      cleanLine=cleanLine[0:idx]
    
    if not cleanLine:
      continue
    
    # collapse multi-spaces
    sizeChanged = True
    while (sizeChanged):
      sizeBefore = len(cleanLine)
      cleanLine = cleanLine.replace('  ',' ')
      sizeAfter = len(cleanLine)
      if (sizeBefore == sizeAfter):
        sizeChanged = False
    
    if cleanLine.startswith("otb_module("):
      isInModDef = True
    
    if isInModDef:
      lineBuffer = lineBuffer + cleanLine + " "
      lineList.append(line)
    
    if cleanLine.endswith(')'):
      # parse buffer
      if isInModDef:
        words = (lineBuffer[11:-2]).split(' ')
        modName = words[0]
        if modName.startswith('OTB'):
          modName = modName[3:]
        if "DEPENDS" in words:
          pos = words.index("DEPENDS") + 1
          while (pos < len(words)):
            if words[pos] in keywords:
              break
            curDep = (words[pos])[3:]
            depList[curDep] = []
            pos += 1
        if "OPTIONAL_DEPENDS" in words:
          pos = words.index("OPTIONAL_DEPENDS") + 1
          while (pos < len(words)):
            if words[pos] in keywords:
              break
            curDep = (words[pos])[3:]
            optDepList[curDep] = []
            pos += 1
        if "TEST_DEPENDS" in words:
          pos = words.index("TEST_DEPENDS") + 1
          while (pos < len(words)):
            if words[pos] in keywords:
              break
            curDep = (words[pos])[3:]
            testDepList[curDep] = []
            pos += 1
        isInModDef = False
        lineBuffer = ""
        lineList = []
  
  fd.close()
  return [depList , optDepList, testDepList]

def parseOTBModuleCmake(path):
  depends = {}
  optDepends = {}
  testDepends = {}
  for grpDir in os.listdir(path):
    grpPath = op.join(path,grpDir)
    if not op.isdir(grpPath):
      continue
    for modDir in os.listdir(grpPath):
      modPath = op.join(grpPath,modDir)
      if not op.isdir(modPath):
        continue
      otbModuleCmake = op.join(modPath,"otb-module.cmake")
      if not op.isfile(otbModuleCmake):
        # not a valid OTB module
        continue
      # parse module declaration
      [depList , optDepList, testDepList] = parseModuleDefinition(otbModuleCmake)
      depends[modDir] = depList
      optDepends[modDir] = optDepList
      testDepends[modDir] = testDepList
  return [depends , optDepends, testDepends]

def parseModuleRoot(path):
  sourceList = {}
  testList = {}
  moduleList = {}
  groups = {}
  codeExt = [".h",".hpp",".hxx",".c",".cpp",".cxx",".txx"]
  
  for grpDir in os.listdir(path):
    grpPath = op.join(path,grpDir)
    if not op.isdir(grpPath):
      continue
    for modDir in os.listdir(grpPath):
      modPath = op.join(grpPath,modDir)
      if not op.isdir(modPath):
        continue
      if not grpDir in groups:
        groups[grpDir] = {}
      groups[grpDir][modDir] = 1
      moduleList[modDir] = []
      # parse sources
      subDir_src = op.join(modPath,'src')
      subDir_inc = op.join(modPath,'include')
      subDir_app = op.join(modPath,'app')
      subDir_test = op.join(modPath,'test')
      for dirPath, dirNames, fileNames in os.walk(modPath):
        for fileName in fileNames:
          ext = (op.splitext(fileName))[1]
          if not ext in codeExt:
            continue
          shortPath = dirPath.replace(path,'Modules',1)
          if  dirPath.startswith(subDir_test):
            testList[op.join(shortPath,fileName)] = modDir
          else:
            # check for duplicated source names
            if fileName in sourceList:
              print "Warning : duplicated source name : "+fileName
            sourceList[fileName] = modDir
            moduleList[modDir].append(op.join(shortPath,fileName))

  return [groups,moduleList,sourceList,testList]

def searchAllIncludes(path):
  includes = []
  
  ifstream = open(path)
  lines = ifstream.readlines()
  ifstream.close()
  
  search_string=r'^#include *([<"])([^<"]+)([>"])'
  includeRegexp=re.compile(search_string)
  
  for line in lines:
    gg = includeRegexp.match(line)
    if (gg != None) and (len(gg.groups()) == 3):
      includes.append(gg.group(2))
  return includes

def analyseInclude(inc,sourceList):
  result = "other"
  systemInc = ["string.h","stdio.h","stdint.h","ctype.h","dirent.h",  \
    "assert.h","sys/types.h","stdlib.h","time.h","memory.h","math.h",\
    "io.h","signal.h","fcntl.h","mex.h","winsock2.h","pmmintrin.h",\
    "emmintrin.h","windows.h","unistd.h","errno.h","stddef.h","float.h",\
    "string","iostream","vector","fstream","map","algorithm","typeinfo",\
    "cassert","iterator","complex","numeric","iomanip","cmath","stdio",\
    "cstdlib","cstdio","iosfwd","sstream","limits","utility","exception",\
    "list","deque","set","cstring","stdexcept","clocale","ostream"]
  
  baseInc = op.basename(inc)
  hasUnderScore = bool(baseInc.count("_"))
  extInc = (op.splitext(baseInc))[1]
  
  if (inc in systemInc) or inc.startswith("sys/"):
    result = "system"
  elif baseInc.startswith("otb") and (not hasUnderScore) and (extInc in [".h",".txx"]):
    if baseInc in sourceList:
      result = sourceList[baseInc]
    elif baseInc == "otbConfigure.h":
      result = "Common"
    else:
      print "OTB header not found : "+inc
  elif baseInc.startswith("itk"):
    if baseInc in sourceList:
      result = sourceList[baseInc]
    else:
      result = "ITK"
  elif baseInc[0:3] in ["vcl","vnl"]:
    result = "ITK"
  elif inc.startswith("itksys"):
    result = "ITK"
  elif (inc.find("gdal") == 0) or (inc.find("ogr") == 0) or (inc.find("cpl_") == 0):
    result = "GDAL"
  elif (inc.find("ossim") == 0):
    result = "Ossim"
  elif (inc.find("opencv") == 0):
    result = "OpenCV"
  elif (inc.find("muParser") == 0):
    result = "MuParser"
  elif (inc.find("mpParser") == 0):
    result = "MuParserX"
  elif (inc.find("boost") == 0):
    if (inc == "boost/type_traits/is_contiguous.h"):
      result = "BoostAdapters"
    else:
      result = "Boost"
  elif (inc.find("tinyxml") == 0) or (inc == "otb_tinyxml.h"):
    result = "TinyXML"
  elif (inc.find("mapnik") == 0):
    result = "Mapnik"
  elif (inc.find("kml") == 0):
    result = "libkml"
  elif (inc.find("curl") == 0) or (inc == "otb_curl.h"):
    result = "Curl"
  elif (inc.find("msImageProcessor") == 0):
    result = "Edison"
  elif (inc.find("openjpeg") == 0) or inc.startswith("opj_"):
    result = "OpenJPEG"
  elif (inc.find("siftfast") == 0):
    result = "SiftFast"
  elif (inc.find("svm") == 0):
    result = "LibSVM"
  elif (inc.find("expat") >= 0):
    result = "Expat"
  elif ((inc.lower()).find("6s") >= 0):
    result = "6S"
  elif (inc.find("openthread") == 0) or inc.startswith("OpenThreads/"):
    result = "OpenThread"
  elif (baseInc == "ConfigFile.h"):
    result = "ConfigFile"
  elif inc in ["QtCore","QtGui","QString","QObject"]:
    result = "Qt4"
  elif baseInc in sourceList:
    result = sourceList[baseInc]
  
  return result

def buildModularDep(otbDir,moduleList,sourceList):
  depList = {}
  for mod in moduleList.keys():
    dependance = {}
    for src in moduleList[mod]:
      srcFullPath = op.join(otbDir,src)
      srcIncludes = searchAllIncludes(srcFullPath)
      for inc in srcIncludes:
        res = analyseInclude(inc,sourceList)
        if res == "system":
          continue
        if (res in moduleList):
          if res == mod:
            continue
          if not dependance.has_key(res):
            dependance[res] = []
          dependance[res].append({"from":op.basename(src) , "to":inc})
        else:
          print "Unknown dependency : "+inc
    
    depList[mod] = dependance
  # Some adjustments
  for mod in depList:
    if mod == "OSSIM":
      if not "OpenThreads" in depList[mod]:
        depList[mod]["OpenThreads"] = []
  
  return depList

def cleanDepList(depList,fullDepList):
  # clean full dependencies : 
  # - if module 'a' depends on 'b' 'c' and 'd'
  # - if module 'b' depens on 'd'
  # - if 'b' and 'd' are clean
  #   -> then remove 'd' from 'a' dependency list
  # it will be considered as inherited from 'b'
  cleanDepList = {}
  for mod in depList.keys():
    cleanDepList[mod] = {}
    depListToRemove = []
    for dep1 in depList[mod]:
      for dep2 in depList[mod]:
        if dep2 == dep1:
          continue
        if not dep1 in fullDepList:
          continue
        if (dep2 in fullDepList[dep1]) and \
           (not dep2 in depListToRemove):
          depListToRemove.append(dep2)
    for dep in depList[mod]:
      if not dep in depListToRemove:
        cleanDepList[mod][dep] = 1
  return cleanDepList
  
def updateSourceList(path,varName,added,removed):  
  fd = open(path,'rb')
  newContent = []
  indent = "  "
  isInSetSrc = False
  for line in fd:
    cleanLine = line.strip(' \n\t\r')
    if isInSetSrc and line.count(')') == 1:
      # detect indentation
      pos = line.find(cleanLine)
      if indent != line[0:pos]:
        indent = line[0:pos]
      # append new entries
      for item in added:
        newContent.append(indent+item+"\n")
      isInSetSrc = False
    
    if isInSetSrc:
      if cleanLine in removed:
        continue
    
    if line.startswith("set("+varName):
      isInSetSrc = True
    newContent.append(line)
  fd.close()
  
  fd = open(path,'wb')
  fd.writelines(newContent)
  fd.close()

def updateTestDriver(path,added,removed):
  fd = open(path,'rb')
  newContent = []
  indent = "  "
  isInRegister = False
  previousLine = ""
  for line in fd:
    cleanLine = line.strip(' \n\t\r')
    if isInRegister and line.count('}') == 1:
      # append new entries
      for item in added:
        registerItem = item.replace(".cxx","")
        registerItem = "REGISTER_TEST("+registerItem+");"
        newContent.append(indent+registerItem+"\n")
      isInRegister = False
    
    if isInRegister:
      curSourceTest = cleanLine.replace("REGISTER_TEST(","")
      curSourceTest = curSourceTest.replace(");","")
      curSourceTest = curSourceTest+".cxx"
      if curSourceTest in removed:
        continue
    
    if line.count('{') and \
      (("RegisterTests()" in line) or ("RegisterTests()" in previousLine)):
      isInRegister = True
    
    previousLine = line
    newContent.append(line)
  fd.close()
  
  fd = open(path,'wb')
  fd.writelines(newContent)
  fd.close()


def initializeSrcCMakeLists(path,modName):
  fd = open(path,'wb')
  fd.write("set(OTB"+modName+"_SRC\n")
  fd.write("  )\n")
  fd.write("\n")
  fd.write("add_library(OTB"+modName+" ${OTB"+modName+"_SRC})\n")
  fd.write("target_link_libraries(OTB"+modName+"\n")
  fd.write("# Fill with libraries from DEPENDS list")
  fd.write(")\n")
  fd.write("\n")
  fd.write("otb_module_target(OTB"+modName+")\n")
  fd.close()

def initializeTestCMakeLists(path,modName):
  fd = open(path,'wb')
  fd.write("otb_module_test()\n")
  fd.write("set(OTB"+modName+"Tests\n")
  fd.write("  otb"+modName+"TestDriver.cxx")
  fd.write("  )\n")
  fd.write("\n")
  fd.write("add_executable(otb"+modName+"TestDriver ${OTB"+modName+"Tests})\n")
  fd.write("target_link_libraries(otb"+modName+"TestDriver ${OTB"+modName+"-Test_LIBRARIES})\n")
  fd.write("otb_module_target_label(otb"+modName+"TestDriver)\n")
  fd.close()

def initializeTestDriver(path):
  fd = open(path,'wb')
  fd.write("#include \"otbTestMain.h\"\n")
  fd.write("void RegisterTests()\n")
  fd.write("{\n")
  fd.write("}\n")
  fd.close()

def moveTestCode(srcPath,dstPath,testCode):
  
  # First, process destination CMakeLists.txt
  dst = open(dstPath,'rb')
  new_dst_content = dst.readlines()
  
  for test,test_body in testCode.iteritems():
    for line in test_body['code']:
      new_dst_content.append(line)
  dst.close()

  dst = open(dstPath,'w')
  dst.writelines(new_dst_content)
  dst.close()

  # Second, process source CMakeLists.txt

  src = open(srcPath,'rb')
  new_src_content = src.readlines()

  for test,test_body in testCode.iteritems():
    id = 0
    start = -1
    for line in new_src_content:
      if line == test_body['code'][0]:
        start = id
        break
      id+=1
    if start > 0:
      del new_src_content[start:start+len(test_body['code'])]
  
  src.close()

  src = open(srcPath,'w')
  src.writelines(new_src_content)
  src.close()


#----------------- MAIN ---------------------------------------------------
def main(argv):
  otbDir = op.abspath(argv[1])
  targetModule = argv[2]
  targetGroup = "TBD"
  if targetModule.count('/') == 1:
    pos = targetModule.find('/')
    targetGroup = targetModule[0:pos]
    targetModule = targetModule[pos+1:]
  if targetModule == "":
    print "Wrong module name, check input argument : "+argv[2]
  if targetGroup == "":
    print "Wrong group name, check input argument : "+argv[2]
  
  srcFiles = []
  for item in argv[3:]:
    if op.isfile(op.join(otbDir,item)):
      srcFiles.append(item.strip('./'))
    else:
      print "Input source file not found, will be skipped : "+item
  
  # First, analyse current OTB tree, retrieve :
  #  - module list
  #  - group vs module association
  #  - module dependency graph from otb-module.cmake
  modulesRoot = op.join(otbDir,"Modules")
  
  [depList, optDepList, testDepList] = parseOTBModuleCmake(modulesRoot)
  fullDepList = manifestParser.buildFullDep(depList)
  oldCleanDepList = cleanDepList(depList,fullDepList)
  
  [groups,moduleList,sourceList,testList] = parseModuleRoot(modulesRoot)
  
  # DEBUG
  #manifestParser.printDepList(depList)
  #print str(moduleList)
  
  
  # Second, operate the move
  if targetModule in moduleList:
    targetGroup = manifestParser.getGroup(targetModule,groups)
  else:
    if targetGroup == 'TBD':
      print "Error : group name must be specified for new modules (use group/module syntax)"
      return 1
  
  destinationPrefix = op.join(targetGroup,targetModule)
  for srcFile in srcFiles:
    cleanFile = srcFile.strip('./')
    words = cleanFile.split('/')
    srcMod = words[2]
    srcGrp = words[1]
    targetFile = cleanFile.replace(srcGrp+'/'+srcMod,destinationPrefix,1)
    targetPath = op.join(otbDir,op.dirname(targetFile))
    if not op.isdir(targetPath):
      os.makedirs(targetPath)
    shutil.move(op.join(otbDir,cleanFile),targetPath)
  
  # Compute new modules dependencies
  [newGroups,newModuleList,newSourceList,newTestList] = parseModuleRoot(modulesRoot)
  newDepList = buildModularDep(otbDir,newModuleList,newSourceList)
  
  # DEBUG
  #manifestParser.printDepList(newDepList)
  
  # compute full dependencies
  newFullDepList = manifestParser.buildFullDep(newDepList)
  
  # detect cyclic dependencies
  cyclicDependentModules = []
  for mod in newFullDepList.keys():
    if mod in newFullDepList[mod]:
      if not mod in cyclicDependentModules:
        cyclicDependentModules.append(mod)
  if len(cyclicDependentModules) > 0:
    print "Check for cyclic dependency :"
    for mod in cyclicDependentModules:
      print "  -> "+mod+" depends on : "
      print "      "+str(newFullDepList[mod])
    return 1
  else:
    print "Check for cyclic dependency : OK"
  
  newCleanDepList = newDepList #cleanDepList(newDepList,newFullDepList)
  
  # Analyse tests
  testCxx = {}
  for test in newTestList:
    testPath = op.join(otbDir,test)
    res = createTestManifest.parseTestCxx(testPath)
    if res["isTestDriver"]:
      # no need to dispatch test drivers, they can be generated again
      continue
    [newTestDepList,newThirdPartyDep] = createTestManifest.getTestDependencies(res["includes"],newSourceList)
    curGroup = manifestParser.getGroup(newTestList[test],newGroups)
    if not res["hasMain"]:
      # manually add dependency to TestKernel for cxx using a test driver
      # the include to otbTestMain.h header is not located in the cxx
      newTestDepList["TestKernel"] = {"from":test ,"to":"Modules/IO/TestKernel/include/otbTestMain.h"}
    testCxx[test] = {"depList":newTestDepList , \
                     "thirdPartyDep":newThirdPartyDep, \
                     "group":curGroup, \
                     "module":newTestList[test], \
                     "res":res}
  
  allTestDepends = createTestManifest.gatherTestDepends(testCxx,newFullDepList)
  
  # clean the test depends (i.e. ImageIO is dragged by TestKernel)
  cleanTestDepends = {}
  for mod in allTestDepends:
    cleanTestDepends[mod] = {}
    for dep1 in allTestDepends[mod]:
      isClean = True
      for dep2 in allTestDepends[mod]:
        if dep1 == dep2:
          continue
        if dep1 in newFullDepList[dep2]:
          isClean = False
          break
      if isClean:
        cleanTestDepends[mod][dep1] = 1
  
  # give hints on modifications to perform on DEPENDS and TEST_DEPENDS
  for mod in newDepList:
    curGroup = manifestParser.getGroup(mod,newGroups)
    if mod in depList:
      if 'ITK' in newDepList[mod]: del newDepList[mod]['ITK']
      if bool(sorted(newDepList[mod].keys()) != sorted(depList[mod].keys())):
        print "Module "+mod+"  -> DEPENDS differ : "+str(depList[mod].keys())+" then "+str(newDepList[mod].keys())
      if mod in cleanTestDepends and mod in testDepList:
        if bool(sorted(cleanTestDepends[mod].keys()) != sorted(testDepList[mod].keys())):
          print "Module "+mod+"  -> TEST_DEPENDS differ : "+str(testDepList[mod].keys())+" then "+str(cleanTestDepends[mod].keys())
    else:
      print "Module "+mod+" new !"
      if mod in newCleanDepList:
        print "  -> DEPENDS : "+str(newCleanDepList[mod].keys())
      if mod in cleanTestDepends:
        print "  -> TEST_DEPENDS : "+str(cleanTestDepends[mod].keys())
    
    #  - fix the otb-module.cmake ?
    #  - fix the target_link_libraries ?
  
  # fix srcList and test declaration
  os.chdir(otbDir)
  for srcFile in srcFiles:
    cleanFile = srcFile.strip('./')
    words = cleanFile.split('/')
    srcMod = words[2]
    srcGrp = words[1]
    srcSub = words[3]
    targetFile = cleanFile.replace(srcGrp+"/"+srcMod,destinationPrefix,1)
    #  - for input files in 'src' : adapt OTBModule_SRC
    if srcSub == "src" and len(words) == 5:
      # remove entry in previous module
      removed = [op.basename(srcFile)]
      added = []
      cmakelistPath = op.join(modulesRoot,op.join(srcGrp,op.join(srcMod,"src/CMakeLists.txt")))
      updateSourceList(cmakelistPath,"OTB"+srcMod+"_SRC",added,removed)
      # add entry in target module
      removed = []
      added = [op.basename(srcFile)]
      cmakelistPath = op.join(modulesRoot,op.join(destinationPrefix,"src/CMakeLists.txt"))
      if not op.exists(cmakelistPath):
        initializeSrcCMakeLists(cmakelistPath,targetModule)
        call(["hg","add",cmakelistPath.replace(otbDir,".")])
      updateSourceList(cmakelistPath,"OTB"+targetModule+"_SRC",added,removed)
    if srcSub == "test" and len(words) == 5:
      if testCxx[targetFile]["res"]["hasMain"]:
        print "Test with main ("+targetFile+") : not handled for now"
      else:
        # remove entry in previous module source list
        removed = [op.basename(srcFile)]
        added = []
        oldCmakelistPath = op.join(modulesRoot,op.join(srcGrp,op.join(srcMod,"test/CMakeLists.txt")))
        oldTestDriverPath = op.join(modulesRoot,op.join(srcGrp,op.join(srcMod,"test/otb"+srcMod+"TestDriver.cxx")))
        updateSourceList(oldCmakelistPath,"OTB"+srcMod+"Tests",added,removed)
        updateTestDriver(oldTestDriverPath,added,removed)
        # add entry in target module source list
        removed = []
        added = [op.basename(srcFile)]
        cmakelistPath = op.join(modulesRoot,op.join(destinationPrefix,"test/CMakeLists.txt"))
        testDriverPath = op.join(modulesRoot,op.join(destinationPrefix,"test/otb"+targetModule+"TestDriver.cxx"))
        if not op.exists(cmakelistPath):
          # there was no test before : initialize CMakeLists.txt
          initializeTestCMakeLists(cmakelistPath,targetModule)
          call(["hg","add",cmakelistPath.replace(otbDir,".")])
        if not op.exists(testDriverPath):
          # there was no test before : initialize test driver
          initializeTestDriver(testDriverPath)
          call(["hg","add",testDriverPath.replace(otbDir,".")])
        updateSourceList(cmakelistPath,"OTB"+targetModule+"Tests",added,removed)
        updateTestDriver(testDriverPath,added,removed)
        
        #  - move test declaration
        testCode = dispatchTests.findTestFromExe(oldCmakelistPath,"otb"+srcMod+"TestDriver","",testCxx[targetFile]["res"]["testFunctions"],'otb_')

        print "Found "+str(len(testCode))+" tests to move"

        moveTestCode(oldCmakelistPath,cmakelistPath,testCode)
    
  
  # perform hg rename -A
  for srcFile in srcFiles:
    cleanFile = srcFile.strip('./')
    words = cleanFile.split('/')
    srcMod = words[2]
    srcGrp = words[1]
    targetFile = cleanFile.replace(srcGrp+'/'+srcMod,destinationPrefix,1)
    call(["hg","rename","-A",cleanFile,targetFile])
    
  # TODO : hg commit by the user
  
  


if __name__ == "__main__":
  if len(sys.argv) < 4 :
    showHelp()
  else:
    main(sys.argv)

