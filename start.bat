echo "start fast api service...."
set PYTHONPATH=%cd%/fast_api_repo
uvicorn fast_api_repo.main:app
echo "start fast api finish...."