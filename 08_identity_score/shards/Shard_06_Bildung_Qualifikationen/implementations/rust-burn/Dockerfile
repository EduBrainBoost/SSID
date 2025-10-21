# Multi-stage Rust build for Burn ML framework
FROM rust:1.75-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y     pkg-config     libssl-dev     && rm -rf /var/lib/apt/lists/*

# Copy Cargo files
COPY Cargo.toml Cargo.lock ./

# Build dependencies (cached layer)
RUN mkdir src &&     echo "fn main() {}" > src/main.rs &&     cargo build --release &&     rm -rf src

# Copy source code
COPY . .

# Build application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y     ca-certificates     libssl3     && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /app/target/release/app /usr/local/bin/app

# Non-root user
RUN useradd -m -u 1000 appuser &&     chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3     CMD ["curl", "-f", "http://localhost:8080/health", "|", "exit 1"]

EXPOSE 8080

CMD ["app"]
