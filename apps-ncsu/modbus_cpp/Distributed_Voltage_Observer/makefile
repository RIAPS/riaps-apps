SHELL := /bin/bash
CMAKE := $(shell which cmake 2> /dev/null)
CLANG-FORMAT := $(shell which clang-format 2> /dev/null)
RM-CMD := $(shell which rm 2> /dev/null)
all:
package:

ifneq ("$(wildcard CMakeLists.txt)","")
realclean:
ifndef RM-CMD
	rmdir build /s /q
else
	$(shell rm -rf build)
endif

build/armhf/Makefile: CMakeLists.txt
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	mkdir -p build/armhf/
	cd build/armhf/ && \
	cmake -Darch=armhf -DCMAKE_INSTALL_PREFIX="/"  ../..
	@echo "done"
endif

build/arm64/Makefile: CMakeLists.txt
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	mkdir -p build/arm64/
	cd build/arm64/ && \
	cmake -Darch=arm64 -DCMAKE_INSTALL_PREFIX="/"  ../..
	@echo "done"
endif

build/amd64/Makefile: CMakeLists.txt
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	mkdir -p build/amd64/
	cd build/amd64/ && \
	cmake -Darch=amd64  -DCMAKE_INSTALL_PREFIX="/" ../..
	@echo "done"
endif

all-amd64: build/amd64/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/amd64/ -j2
endif

all-armhf: build/armhf/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/armhf -j2
endif

all-arm64: build/arm64/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/arm64 -j2
endif


clean-armhf: build/armhf/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/armhf clean -j2
endif

clean-arm64: build/armhf/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/arm64 clean -j2
endif

clean-amd64: build/amd64/Makefile
ifndef CMAKE
	$(error "cmake is not available. Please install")
else
	make -C build/amd64 clean -j2
endif

reformat:
ifndef CLANG-FORMAT
	$(error "clang-format is not available. Please install")
else
	find . -iname *.h -o -iname *.cc -o -iname *.cpp | xargs clang-format -i -style=file
endif
else
realclean:
	@echo "This is a python only project. Build command do not apply"
reformat:
	@echo "This is a python only project. Build command do not apply"
all-armhf:
	@echo "This is a python only project. Build command do not apply"
all-amd64:
	@echo "This is a python only project. Build command do not apply"
endif
