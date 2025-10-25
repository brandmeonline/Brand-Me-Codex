# Copyright (c) Brand.Me, Inc. All rights reserved.
# Base image for ai-brain-hub and policy-safety services.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "ai_brain_hub.main:app", "--host", "0.0.0.0", "--port", "8000"]
# To run policy-safety instead:
# CMD ["uvicorn", "policy_safety.main:app", "--host", "0.0.0.0", "--port", "8001"]
