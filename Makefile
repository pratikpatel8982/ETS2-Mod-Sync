# ===== Configuration =====
VENV = .venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip

# ===== Default target =====
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make venv        Create virtual environment"
	@echo "  make deps        Install Python + Rust deps"
	@echo "  make build       Build Rust native module"
	@echo "  make run         Run the application"
	@echo "  make clean       Clean build artifacts"

# ===== Virtual environment =====
.PHONY: venv
venv:
	python -m venv $(VENV)

# ===== Dependencies =====
.PHONY: deps
deps: venv
	$(PIP) install --upgrade pip
	$(PIP) install maturin PySide6

# ===== Build native Rust module =====
.PHONY: build
build:
	cd decryptor && maturin develop

# ===== Run app =====
.PHONY: run
run:
	$(PYTHON) main.py

# ===== Cleanup =====
.PHONY: clean
clean:
	cd decryptor && cargo clean
