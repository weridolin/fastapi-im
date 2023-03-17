echo "migrate database..."
alembic upgrade head
echo "migrate finish..."
echo "start fast api service...."
export PYTHONPATH="./fast_api_repo"
uvicorn fast_api_repo.main:app