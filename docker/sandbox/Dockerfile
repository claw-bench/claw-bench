FROM claw-bench-base:latest

LABEL maintainer="Claw Bench Contributors"
LABEL description="Sandboxed execution environment for claw-bench tasks"

# Create a non-root user for task execution
RUN groupadd -r sandbox && useradd -r -g sandbox -m -s /bin/bash sandbox

# Create standard directories
RUN mkdir -p /workspace /task /output && \
    chown -R sandbox:sandbox /workspace /task /output

# Security: drop all capabilities by default
# Network access is disabled at the Docker run level via --network=none

# Set resource limits via ulimit defaults
RUN echo "sandbox soft nproc 256" >> /etc/security/limits.conf && \
    echo "sandbox hard nproc 512" >> /etc/security/limits.conf && \
    echo "sandbox soft nofile 1024" >> /etc/security/limits.conf && \
    echo "sandbox hard nofile 4096" >> /etc/security/limits.conf

# Switch to non-root user
USER sandbox
WORKDIR /workspace

# Default entrypoint runs the task setup then waits for commands
ENTRYPOINT ["/bin/bash"]
CMD ["-c", "echo 'Sandbox ready'; exec bash"]
