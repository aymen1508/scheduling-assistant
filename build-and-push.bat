@echo off
REM Configuration
set REGISTRY_NAME=vikaraassistantdemo
set RESOURCE_GROUP=assistant-demo
set IMAGE_NAME=vikara-backend
set IMAGE_TAG=latest

echo === Building Docker Image ===
docker build -t %IMAGE_NAME%:%IMAGE_TAG% -f Dockerfile .

if %errorlevel% neq 0 (
    echo X Build failed
    exit /b 1
)

echo Built successfully!
echo.
echo === Tagging Image for Azure ===
docker tag %IMAGE_NAME%:%IMAGE_TAG% %REGISTRY_NAME%.azurecr.io/%IMAGE_NAME%:%IMAGE_TAG%

echo.
echo === Pushing to Azure Container Registry ===
echo Make sure you're logged in: az acr login --name %REGISTRY_NAME%
docker push %REGISTRY_NAME%.azurecr.io/%IMAGE_NAME%:%IMAGE_TAG%

if %errorlevel% neq 0 (
    echo X Push failed
    exit /b 1
)

echo.
echo Pushed successfully!
echo Image URI: %REGISTRY_NAME%.azurecr.io/%IMAGE_NAME%:%IMAGE_TAG%
