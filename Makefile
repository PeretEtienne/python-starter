build:
	@echo "Building services..."
	docker compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . build

run: down
	@echo "Starting services..."
	docker compose -f docker-compose.yml -f deploy/docker-compose.dev.yml up -d --remove-orphans

down:
	@echo "Stopping services..."
	docker compose -f docker-compose.yml -f deploy/docker-compose.dev.yml down
