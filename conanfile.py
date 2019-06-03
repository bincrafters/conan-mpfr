# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class MpfrConan(ConanFile):
    name = "mpfr"
    version = "4.0.2"
    description = "The MPFR library is a C library for multiple-precision floating-point computations with " \
                  "correct rounding"
    topics = ("conan", "mpfr", "multiprecision", "math", "mathematics")
    url = "https://github.com/bincrafters/conan-mpfr"
    homepage = "https://www.mpfr.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "LGPL-3.0-or-later"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    requires = "gmp/6.1.2@bincrafters/stable"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        source_url = "https://ftp.gnu.org/gnu/mpfr/mpfr-%s.tar.bz2" % self.version
        tools.get(source_url, sha256="c05e3f02d09e0e9019384cdd58e0f19c64e6db1fd6f5ecf77b4b1c61ca253acc")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            args = ["--enable-thread-safe"]
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--disable-static"])
            if self.settings.compiler == "clang":
                # warning: optimization flag '-ffloat-store' is not supported
                args.append("mpfr_cv_gcc_floatconv_bug=no")
            if self.settings.compiler == "clang" and self.settings.arch == "x86":
                # fatal error: error in backend: Unsupported library call operation!
                args.append("--disable-float128")
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make(args=["V=0"])
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        la = os.path.join(self.package_folder, "lib", "libmpfr.la")
        if os.path.isfile(la):
            os.unlink(la)

    def package_info(self):
        self.cpp_info.libs = ["mpfr"]
