# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define with_maven 0
%define without_maven 1

%define parent plexus
%define subname bsh-factory

Name:           %{parent}-%{subname}
Version:        1.0
Release:        0.5.a7s.1.13
Summary:        Plexus Bsh component factory
License:        MIT
Group:          Development/Java
URL:            http://plexus.codehaus.org/
Source0:        %{name}-src.tar.gz
# svn export svn://svn.plexus.codehaus.org/plexus/tags/plexus-bsh-factory-1.0-alpha-7-SNAPSHOT plexus-bsh-factory/
# tar czf plexus-bsh-factory-src.tar.gz plexus-bsh-factory/
Source1:        %{name}-jpp-depmap.xml
Source2:        %{name}-build.xml
Source3:	plexus-bsh-factory-license.txt

Patch1:         %{name}-encodingfix.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:     jpackage-utils >= 0:1.7.2
%if %{with_maven}
BuildRequires:     maven2 >= 2.0.4-9
BuildRequires:     maven2-plugin-compiler
BuildRequires:     maven2-plugin-install
BuildRequires:     maven2-plugin-jar
BuildRequires:     maven2-plugin-javadoc
BuildRequires:     maven2-plugin-resources
BuildRequires:     maven2-plugin-surefire
BuildRequires:     maven2-common-poms >= 1.0-2
%else
BuildRequires:     ant
%endif
BuildRequires:     bsh
BuildRequires:     classworlds
BuildRequires:     plexus-container-default
BuildRequires:     plexus-utils

Requires:          bsh
Requires:          classworlds
Requires:          plexus-container-default
Requires:          plexus-utils

Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%description
Bsh component class creator for Plexus.

%if %{with_maven}
%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.
%endif

%prep
%setup -q -n %{name}

%patch1 -b .sav

%if %{without_maven}
    cp -p %{SOURCE2} build.xml
%endif

cp -p %{SOURCE3} .

%build

%if %{with_maven}
    export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
    mkdir -p $MAVEN_REPO_LOCAL

    mvn-jpp \
        -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc

%else

    mkdir lib
    build-jar-repository \
                             -s -p \
                             lib bsh classworlds \
                             plexus/container-default \
                             plexus/utils
    ant -Dmaven.mode.offline=true

%endif

%install
rm -rf %{buildroot}
# jars
install -d -m 755 %{buildroot}%{_javadir}/plexus
install -pm 644 target/*.jar \
      %{buildroot}%{_javadir}/%{parent}/%{subname}-%{version}.jar
%add_to_maven_depmap org.codehaus.plexus %{name} 1.0-alpha-7 JPP/%{parent} %{subname}

(cd %{buildroot}%{_javadir}/%{parent} && for jar in *-%{version}*; \
  do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

# pom
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 \
  pom.xml %{buildroot}%{_datadir}/maven2/poms/JPP.%{parent}-%{subname}.pom

# javadoc
%if %{with_maven}
    install -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}

    cp -pr target/site/apidocs/* \
        %{buildroot}%{_javadocdir}/%{name}-%{version}/

    ln -s %{name}-%{version} \
                %{buildroot}%{_javadocdir}/%{name} # ghost symlink
%endif

%clean
rm -rf %{buildroot}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc plexus-bsh-factory-license.txt
%dir %{_javadir}/plexus
%{_javadir}/plexus
%{_datadir}/maven2
%{_mavendepmapfragdir}

%if %{with_maven}
%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*
%endif

