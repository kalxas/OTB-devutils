#!/usr/bin/env python3

import subprocess

def run_otb(cmd, prefix):
    cmd = prefix + ";" + cmd

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    outs, errs = p.communicate()

    return outs.decode("utf-8")

def indent(string):
    if string == "":
        return "    [no output]"

    if string.endswith("\n"):
        # Dont indent the terminating endline
        string = string[:-1]
    else:
        raise ValueError("expecting end line terminated string")

    lines = string.split("\n")
    return "\n".join(["    " + l for l in lines])

all_entries = [

("IO Errors", [

    ("Input file does not exist (Convert)",
     "otbcli_Convert -in blabla.tif -out /tmp/out.tif"),

    ("Input file does not exist (ReadImageInfo)",
     "otbcli_ReadImageInfo -in blabla.tif"),

    ("Input file does not exist, with extended filename (Convert)",
     "otbcli_Convert -in 'blabla.tif&bands=1' -out /tmp/out.tif"),

    ("One of the input files does not exist",
     "otbcli_BandMath -il data/QB_1_ortho.tif blabla.tif -out /tmp/out.tif -exp '1'"),

    ("Unsupported input format",
     "otbcli_Convert -in data/svm_model.svm -out /tmp/out.tif"),

    ("Unsupported output format",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.blabla"),

    ("Invalid input image (Convert)",
     "otbcli_Convert -in data/notActuallyTif.tif -out /tmp/out.tif"),

    ("Permission denied (input)",
     "otbcli_Convert -in noReadPermission.png -out /tmp/out.tif"),

    ("Permission denied (output)",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /root/out.tif -progress false"),

    ("Trying to open a directory",
     "otbcli_Convert -in data/DEM_srtm -out /tmp/out.tif"),

]),
("Parameter errors", [

    ("Too many dashes",
     "otbcli_BandMath --il -out /tmp/out.tif -exp '1'"),

    ("Repeated parameter",
     "otbcli_Convert -in data/QB_1_ortho.tif -in data/QB_1_ortho.tif -out /tmp/out.tif -progress false"),

    ("No parameter",
     "otbcli_Convert"),

    ("Non existing parameter",
     "otbcli_Convert -hello world"),

    ("Missing parameter (output)",
     "otbcli_Convert -in data/QB_1_ortho.tif"),

    ("Missing parameter (input)",
     "otbcli_Convert -out /tmp/out.tif"),

    ("Missing parameter value",
     "otbcli_Convert -in -out /tmp/out.tif"),

    ("Empty input image list",
     "otbcli_BandMath -il -out /tmp/out.tif -exp '1'"),

    ("Missing input extension (Convert)",
     "otbcli_Convert -in data/QB_1_ortho -out /tmp/out.tif"),

    ("Missing output extension (Convert)",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out -progress false"),

    ("Empty output filename",
     "otbcli_BandMath -il data/QB_1_ortho.tif -out -exp '1'"),

    ("Invalid extended filename",
     "otbcli_Convert -in data/'QB_1_ortho.tif?&bla=blabla' -out /tmp/out.tif -progress false"),

    ("Parameter syntax error (forgot '-in')",
     "otbcli_Convert data/QB_1_ortho.tif -out /tmp/out.tif"),

    ("Parameter syntax error (forgot '-out')",
     "otbcli_Convert -in data/QB_1_ortho.tif /tmp/out.tif"),

    ("Progress value error",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif -progress false false true"),

    ("Progress value error 2",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif -progress blabla"),

    ("Invalid output type",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif iunt8 -progress false"),

    # TODO
    #("Invalid output type (complex image)",
    #"otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif iunt8 -progress false"),

    ("Too many parameter values (output image)",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif uint8 float double -progress false"),

]),
("Module path errors", [

    ("No module available",
    """OTB_APPLICATION_PATH=""; otbApplicationLauncherCommandLine '' /tmp"""),

    ("Application not available",
    "otbApplicationLauncherCommandLine MakeCoffee"),

    ("Almost nothing (segfault)",
     "otbApplicationLauncherCommandLine ''"),

    ("A bit more than almost nothing",
     "otbApplicationLauncherCommandLine '' /tmp"),

]),
("Application errors", [

    ("RadiometricIndices",
     "otbcli_RadiometricIndices -in data/QB_1_ortho.tif  -out /tmp/out.tif -list blabla"),

    ("PixelValue",
     "otbcli_PixelValue -in ~/cnes/dev/otb-data/Examples/QB_1_ortho.tif -coordx 50 -coordy -6"),

    ("ConcatenateImage",
     "otbcli_ConcatenateImages -il data/QB_1_ortho.tif data/Circle.png -out /tmp/out.tif"),

]),

("Correct parameters", [

    ("ReadImageInfo",
     "otbcli_ReadImageInfo -in data/QB_1_ortho.tif"),

    ("Convert",
     "otbcli_Convert -in data/QB_1_ortho.tif -out /tmp/out.tif -progress false"),

    ("BandMath",
     "otbcli_BandMath -il data/QB_1_ortho.tif -out /tmp/out.tif -exp '1' -progress false"),

    ("BandMathX",
     "otbcli_BandMathX -il data/QB_1_ortho.tif -out /tmp/out.tif -exp '1' -progress false"),

    ("Rescale",
     "otbcli_Rescale -in data/QB_1_ortho.tif -out /tmp/out.tif -progress false"),

    # TODO
    # complex input image
    # complex input image list
    # GDAL derived dataset
    # and too many parameter values (output complex image)

]),

]

if __name__ == "__main__":

    mediawiki_template = ("==== {} ====\n"
                          "''$ {}''\n"
                          "{}\n"
                          "\n"
                          '<div class="mw-collapsible mw-collapsed">\n'
                          "''In debug:''\n"
                          '<div class="mw-collapsible-content">\n'
                          "{}\n"
                          "\n"
                          "</div>\n"
                          "</div>\n"
                          '<div class="mw-collapsible mw-collapsed">\n'
                          "''On release-6.0:\n"
                          '<div class="mw-collapsible-content">\n'
                          "{}\n"
                          "</div>\n"
                          "</div>\n"
                          )

    otb_branch_release = "source ~/cnes/dev/config/env-develop-releasemode.sh"
    otb_branch_debug = "source ~/cnes/dev/config/env-develop.sh"
    otb_develop = "source ~/Téléchargements/OTB-contrib-6.0.0-Linux64/otbenv.profile"

    print("This page is an annex to [[Request_for_Changes-91:_Better_error_messages]]. It contains the full output of the error messages test script.")
    print("")
    print("")
    print("")

    for section, commands in all_entries:
        print("=== {} ===".format(section))

        for comment, cmd in commands:
            out_branch_release = run_otb(cmd, otb_branch_release)
            out_branch_debug = run_otb(cmd, otb_branch_debug)
            out_develop = run_otb(cmd, otb_develop)

            # Render to mediawiki
            print(mediawiki_template.format(
                comment,
                cmd, indent(out_branch_release),
                indent(out_branch_debug),
                indent(out_develop)))
