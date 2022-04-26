FROM $DOCKER_IMAGE

# ------------------- #
#     Preinstall.     #
# ------------------- #

# Make sure provided inputs path exists.
RUN if [ ! -d $INPUTS_PATH ]; then echo "Source directory $INPUTS_PATH not present!" && exit 1; fi

# Make sure outputs path for dependencies is created.
mkdir -p $DOCKER_DEPENDENCIES_OUTPUTS_PATH

# List all insides of inputs and outputs directories.
echo "------------------- $INPUTS_PATH -------------------"
ls -la $INPUTS_PATH
echo "------------------- $DOCKER_OUTPUTS_PATH -------------------"
ls -la $DOCKER_OUTPUTS_PATH

# ------------------- #
#       Install.      #
# ------------------- #

# Run an already pre-built dependencies installation command.
RUN eval $DEPENDENCIES_PIP_INSTALL
# Run an already pre-built requirements.txt installation command.
RUN eval $REQUIREMENTS_PIP_INSTALL

# ------------------- #
#     Postinstall.    #
# ------------------- #

# Just for debugging reasons list what's inside after installation.
RUN echo "------------------- $DOCKER_OUTPUTS_PATH -------------------"
RUN ls -la $DOCKER_OUTPUTS_PATH

# ------------------- #
#       Prebuild.     #
# ------------------- #

# Make sure source output directory exist.
RUN mkdir -p $DOCKER_SOURCE_OUTPUTS_PATH

# ------------------- #
#        Build.       #
# ------------------- #

# Copy source code.
COPY $INPUTS_PATH $DOCKER_SOURCE_OUTPUTS_PATH

# ------------------- #
#      Postbuild.     #
# ------------------- #

# Cleanup.
RUN find $DOCKER_OUTPUTS_PATH -type f -name "*.py[co]" -delete
RUN find $DOCKER_OUTPUTS_PATH -type d -name "__pycache__" -exec rm -rf {{}} +
RUN find $DOCKER_OUTPUTS_PATH -type d -name "*.egg-info" -exec rm -rf {{}} +

# List outputs path contents.
RUN echo "------------------- $DOCKER_DEPENDENCIES_OUTPUTS_PATH ------------------- "
RUN ls -la $DOCKER_DEPENDENCIES_OUTPUTS_PATH
RUN echo "------------------- $DOCKER_SOURCE_OUTPUTS_PATH ------------------- "
RUN ls -la $DOCKER_SOURCE_OUTPUTS_PATH

# Calculate asset-output hash.
RUN echo "------------------- $DOCKER_OUTPUTS_PATH hash ------------------- "
RUN find $DOCKER_OUTPUTS_PATH -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum

# Success!
RUN echo "\n-------------------  build successful ------------------- \n"
