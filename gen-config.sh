#!/usr/bin/env bash
# gen-config.sh — Đọc .env và sinh codebase/config.js
# Chạy: bash gen-config.sh

set -euo pipefail

ENV_FILE="$(dirname "$0")/.env"
OUT_FILE="$(dirname "$0")/codebase/config.js"

if [ ! -f "$ENV_FILE" ]; then
  echo "❌ Không tìm thấy file .env tại: $ENV_FILE"
  exit 1
fi

# Đọc .env, bỏ comment và dòng trống
read_env() {
  local key="$1"
  grep -E "^${key}=" "$ENV_FILE" | head -1 | cut -d'=' -f2-
}

GEMINI_API_KEY=$(read_env "GEMINI_API_KEY")
GEMINI_MODEL=$(read_env "GEMINI_MODEL")
OPENAI_API_KEY=$(read_env "OPENAI_API_KEY")
OPENAI_MODEL=$(read_env "OPENAI_MODEL")
ANTHROPIC_API_KEY=$(read_env "ANTHROPIC_API_KEY")
ANTHROPIC_MODEL=$(read_env "ANTHROPIC_MODEL")
OPENROUTER_API_KEY=$(read_env "OPENROUTER_API_KEY")
OPENROUTER_MODEL=$(read_env "OPENROUTER_MODEL")
ACTIVE_PROVIDER=$(read_env "ACTIVE_PROVIDER")

cat > "$OUT_FILE" << JSEOF
// ⚠️ File này được tự động sinh từ .env bằng gen-config.sh
// ⚠️ KHÔNG commit file này lên GitHub!
// Chạy lại: bash gen-config.sh

const ENV = {
  GEMINI_API_KEY: "${GEMINI_API_KEY}",
  GEMINI_MODEL: "${GEMINI_MODEL:-gemini-2.0-flash}",
  OPENAI_API_KEY: "${OPENAI_API_KEY}",
  OPENAI_MODEL: "${OPENAI_MODEL:-gpt-4o-mini}",
  ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}",
  ANTHROPIC_MODEL: "${ANTHROPIC_MODEL:-claude-sonnet-4-20250514}",
  OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}",
  OPENROUTER_MODEL: "${OPENROUTER_MODEL:-google/gemma-4-31b-it:free}",
  ACTIVE_PROVIDER: "${ACTIVE_PROVIDER:-openrouter}"
};
JSEOF

echo "✅ Đã sinh config.js tại: $OUT_FILE"
echo "   Provider mặc định: ${ACTIVE_PROVIDER:-openrouter}"
