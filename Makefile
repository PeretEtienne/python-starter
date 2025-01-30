build:
	@echo "Building services..."
	docker compose -f docker-compose.yml --project-directory . build

run: down
	@echo "Starting services..."
	docker compose -f docker-compose.yml up -d --remove-orphans

down:
	@echo "Stopping services..."
	docker compose -f docker-compose.yml down

test:
	@echo "Running tests with coverage enforcement..."
	docker compose exec -T api pytest --cov=app/services --cov-fail-under=100

coverage:
	@echo "Running tests with coverage report..."
	docker compose exec -T api pytest --cov=app/services --cov-report=html
