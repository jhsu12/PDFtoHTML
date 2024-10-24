# =================================== #
# Please update the <Basic settings>  #
# =================================== #

## 1. <Basic Settings> 
## (WARNING) WITHOUT [SPACE] as the last word inline!
CONTAINER_NAME := 
VERSION := 1.0.0

## 2. <Deploy Settings> 
DEV_DEPLOY_PROJECT := 
PROD_DEPLOY_PROJECT := 
DEPLOY_REGION := asia-east1


## 3. <Deploy Details>
CONTAINER_MEMORY := 256Mi
ALLOW_UNAUTHENTICATED := true
CONTAINER_ENV_VARS_FILE := .env
# VPC_CONNECTOR_NAME := 
# CLOUD_SQL_INSTANCE := 

## 4. <Local Settings>
LOCAL_PYTHON_CMD := python
LOCAL_SERVER_NAME := app.py
LOCAL_TEST_FILE := test.py

# =============================================================== #
#                             WARNING                             #
# =============================================================== #
# DON'T TOUCH the below unless you understand what you're doing!  #
# =============================================================== #

default:help
.PHONY:default

help:
	@echo make [command]
	@echo ==============
	@echo make help
	@echo '  -> List all commands and tutorial.'
	@echo  
	@echo make git-pull
	@echo '  -> Stash the current changes, pull the latest main/master branch and rebase on it'
	@echo  
	@echo make pytest
	@echo '  -> Change auth config, and do uni-test with [LOCAL_TEST_FILE] by pytest'
	@echo  
	@echo make build
	@echo '  -> Build the container by Docker'
	@echo  
	@echo make deploy
	@echo '  -> Build and Deploy the app onto GCP'
	@echo  
	@echo make clean
	@echo '  -> Clean all cached file in [LOCAL_CACHE_FILE] list'
.PHONY:help

## <Default Env>
DEPLOY_ENV ?= dev

## Artifact Setting
ifeq ($(DEPLOY_ENV), prod)
ARTIFACT_ENV := product
DEPLOY_PROJECT := $(PROD_DEPLOY_PROJECT)
else ifeq ($(DEPLOY_ENV), dev)
ARTIFACT_ENV := develop
DEPLOY_PROJECT := $(DEV_DEPLOY_PROJECT)
else
ARTIFACT_ENV := develop
endif

## Cloud Run Deploy Flag
CLOUD_RUN_FLAGS := --platform managed
ifeq ("$(ALLOW_UNAUTHENTICATED)", true)
CLOUD_RUN_FLAGS += --allow-unauthenticated
else
endif

ifeq ("$(SPECIFIED_SERVICE_ACCOUNT)", "")
else
CLOUD_RUN_FLAGS += --service-account=$(SPECIFIED_SERVICE_ACCOUNT)
endif


ifeq ("$(CONTAINER_MEMORY)", "")
else
CLOUD_RUN_FLAGS += --memory=$(CONTAINER_MEMORY)
endif

ifeq ("$(CLOUD_SQL_INSTANCE)", "")
else
CLOUD_RUN_FLAGS += --set-cloudsql-instances=$(CLOUD_SQL_INSTANCE)
endif

ifeq ("$(VPC_CONNECTOR_NAME)", "")
else
CLOUD_RUN_FLAGS += --vpc-connector $(VPC_CONNECTOR_NAME)
endif

ifeq ("$(CONTAINER_ENV_VARS_FILE)", "")
else

define DOTENV_VARS
awk -F '=' '!/^#/ && NF > 1 {
    if (!first) {
        first = 1;
        printf "%s=%s", $$1, $$2;
    } else {
        printf ",%s=%s", $$1, $$2;
    }
}' ${CONTAINER_ENV_VARS_FILE}
endef
CLOUD_RUN_FLAGS += --set-env-vars $(shell $(DOTENV_VARS))

endif

ARTIFACT_REPO := ${DEPLOY_REGION}-docker.pkg.dev/${DEPLOY_PROJECT}/${ARTIFACT_ENV}
ARTIFACT_REGISTRY_IMAGE ?= ${ARTIFACT_REPO}/${CONTAINER_NAME}:${VERSION}
CONTAINER_REGISTRY_IMAGE ?= gcr.io/${DEPLOY_PROJECT}/${CONTAINER_NAME}

CURR_BRANCH:= $(shell git branch --show-current)
MAIN_BRANCH:= $(shell git branch | grep -E "^main" | sed 's/ \(.*\)/\1/g' )

git-pull: .gitignore CURR_BRANCH MAIN_BRANCH
	@echo ========== git-pull start ==========
ifeq ($(CURR_BRANCH), $(MAIN_BRANCH))
	@echo ----- Step 1 -----
	git stash
	@echo ----- Step 2 -----
	git pull
	@echo ----- Step 3 -----
	git stash pop
else 
	@echo ----- Step 1 -----
	git stash
	@echo ----- Step 2 -----
	git checkout $(MAIN_BRANCH)
	@echo ----- Step 3 -----
	git pull
	@echo ----- Step 4 -----
	git checkout $(CURR_BRANCH)
	@echo ----- Step 5 -----
	git rebase $(MAIN_BRANCH)
	@echo ----- Step 6 -----
	git stash pop
	@echo ========== git-pull finished ==========
endif
.PHONY: pull CURR_BRANCH MAIN_BRANCH

pytest: gcp-auth LOCAL_PYTHON_CMD LOCAL_TEST_FILE
# ${LOCAL_PYTHON_CMD} ${LOCAL_SERVER_NAME} &
	${LOCAL_PYTHON_CMD} -m pytest ${LOCAL_TEST_FILE}
.PHONY: test LOCAL_PYTHON_CMD LOCAL_TEST_FILE

gcp-auth: DEPLOY_PROJECT DEPLOY_REGION
	@echo ========== !!! WARNING !!! ==========
	gcloud config configurations activate ${DEPLOY_PROJECT}
	gcloud auth configure-docker ${DEPLOY_REGION}-docker.pkg.dev
.PHONY:gcp-auth DEPLOY_PROJECT DEPLOY_REGION


open-docker:
ifeq ("$(shell pgrep Docker >/dev/null && echo "true" || echo "false" )", "true")
	@echo ========== Docker Opened ==========
else
	@echo ========== Docker NOT opened ==========
	open --background -a Docker
	@sleep 5
endif


build-docker: ARTIFACT_REGISTRY_IMAGE DEPLOY_REGION open-docker
	gcloud auth configure-docker ${DEPLOY_REGION}-docker.pkg.dev
	docker build --platform linux/amd64 -t ${ARTIFACT_REGISTRY_IMAGE} .
.PHONY:ARTIFACT_REGISTRY_IMAGE DEPLOY_REGION open-docker

build-gcloud: CONTAINER_REGISTRY_IMAGE
	gcloud builds submit --tag ${CONTAINER_REGISTRY_IMAGE} --timeout=3600
.PHONY:  CONTAINER_REGISTRY_IMAGE

build-deploy-gcp: gcp-auth Dockerfile requirements.txt ARTIFACT_REPO CONTAINER_NAME VERSION DEPLOY_PROJECT DEPLOY_ENV ARTIFACT_REGISTRY_IMAGE CONTAINER_REGISTRY_IMAGE
	@echo '===================='
	@echo 'How to build images:'
	@echo '  1) docker build --> Artifact Registry (Recommended)'
	@echo '  2) gcloud build submit --> Container Registry'
	@echo '  3) SKIP build, directly deploy (with current Artifact image)'
	@echo '  4) SKIP build, directly deploy (with current Container Registry image)'
	@while read -e -p 'Choose the build option(1/2/3/4) or Ctrl+C to exit: ' value ;  do \
		case $$value in \
		1) \
			echo "Ready to build by docker" \
			&& $(MAKE) DEPLOY_ENV=$(DEPLOY_ENV) build-docker \
			&& docker push ${ARTIFACT_REGISTRY_IMAGE} \
			&& gcloud run deploy --image ${ARTIFACT_REGISTRY_IMAGE} $(CLOUD_RUN_FLAGS) \
			&& break \
			;;\
		2) \
			echo "Ready to build by gcloud" \
			&& $(MAKE) DEPLOY_ENV=$(DEPLOY_ENV) build-gcloud \
			&& gcloud run deploy --image ${CONTAINER_REGISTRY_IMAGE} $(CLOUD_RUN_FLAGS) \
			&& break \
			;; \
		3) \
			echo "[Warning] Make sure this image existed in Artifact Registry : ${ARTIFACT_REGISTRY_IMAGE}" \
			&& gcloud run deploy --image ${ARTIFACT_REGISTRY_IMAGE} $(CLOUD_RUN_FLAGS) \
			&& break \
			;; \
		4) \
			echo "[Warning] Make sure this image existed in Container Registry : ${CONTAINER_REGISTRY_IMAGE}" \
			&& gcloud run deploy --image ${CONTAINER_REGISTRY_IMAGE} $(CLOUD_RUN_FLAGS) \
			&& break \
			;; \
		esac \
	done;

.PHONY:ARTIFACT_REPO CONTAINER_NAME VERSION DEPLOY_PROJECT DEPLOY_ENV ARTIFACT_REGISTRY_IMAGE CONTAINER_REGISTRY_IMAGE

deploy:
	@echo 'Environment choices:'
	@echo '  dev) ${DEV_DEPLOY_PROJECT}'
	@echo '  prod) ${PROD_DEPLOY_PROJECT}'
	@while read -p 'Where to deploy (dev/prod):' value ;  do \
		case $$value in \
		dev) \
			echo "Ready to deploy on ${DEV_DEPLOY_PROJECT}" \
			&& $(MAKE) DEPLOY_ENV=$$value build-deploy-gcp && break\
			;;\
		prod) \
			echo "Ready to deploy on ${PROD_DEPLOY_PROJECT}" \
			&& $(MAKE) DEPLOY_ENV=$$value build-deploy-gcp && break \
			;; \
		esac \
	done;
.PHONY:deploy

clean: .pytest_cache __pycache__
	-@for cache in $?; do find . -name $$cache | xargs rm -rf ; done
.PHONY:clean