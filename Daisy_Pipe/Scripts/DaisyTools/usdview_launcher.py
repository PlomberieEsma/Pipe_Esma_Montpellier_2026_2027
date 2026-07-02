"""Standalone bootstrap for usdview.

Runs with Prism's embeddable python (its python311._pth ignores PYTHONPATH),
so the import paths are passed as arguments and injected into sys.path here.

usage: python.exe usdview_launcher.py <externalModulesPath> <prismRoot> <usdFile>
"""
import os
import sys


def main():
    extModPath, prismRoot, usdFile = sys.argv[1], sys.argv[2], sys.argv[3]
    usdRoot = os.path.join(extModPath, "USD")
    pysideDir = os.path.join(prismRoot, "PythonLibs", "Python3", "PySide")

    sys.path[:0] = [
        os.path.join(usdRoot, "lib", "python"),              # pxr
        extModPath,                                          # PyOpenGL (OpenGL, OpenGL_accelerate)
        pysideDir,                                           # PySide6 + shiboken6
        os.path.join(prismRoot, "PythonLibs", "Python311"),  # numpy
    ]

    # python >= 3.8 doesn't use PATH to resolve the dlls the pxr .pyds depend on
    dllDirs = [
        os.path.join(usdRoot, "bin"),
        os.path.join(usdRoot, "lib"),
        os.path.join(pysideDir, "PySide6"),
    ]
    for p in dllDirs:
        if os.path.isdir(p):
            os.add_dll_directory(p)
    os.environ["PATH"] = os.pathsep.join(dllDirs + [os.environ.get("PATH", "")])

    import pxr.Usdviewq as Usdviewq

    sys.argv = ["usdview", usdFile]
    try:
        Usdviewq.Launcher().Run()
    except Usdviewq.InvalidUsdviewOption as e:
        print("ERROR: " + str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
