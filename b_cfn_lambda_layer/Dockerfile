# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG DOCKER_IMAGE
FROM $DOCKER_IMAGE

# Inputs path in the parent OS.
ARG INPUTS_PATH

# Output paths within docker container.
ARG OUTPUTS_PATH

# Custom installation command.
ARG PIP_INSTALL

# ------------------- #
#       Prepare.      #
# ------------------- #

# Make sure that the root path of outputs exist.
RUN mkdir -p $OUTPUTS_PATH

# ------------------- #
#       Install.      #
# ------------------- #

# Run an already pre-built dependencies installation command.
RUN eval $PIP_INSTALL

# List outputs directory.
RUN ls -la $OUTPUTS_PATH

# ------------------- #
#        Build.       #
# ------------------- #

# Copy source code.
COPY $INPUTS_PATH $OUTPUTS_PATH

# ------------------- #
#      Postbuild.     #
# ------------------- #

# Cleanup.
RUN find $OUTPUTS_PATH -type f -name "*.py[co]" -delete
RUN find $OUTPUTS_PATH -type d -name "__pycache__" -exec rm -rf {} +
RUN find $OUTPUTS_PATH -type d -name "*.egg-info" -exec rm -rf {} +

# List outputs path contents.
RUN ls -la $OUTPUTS_PATH

# Calculate asset-output hash.
RUN find $OUTPUTS_PATH -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum
