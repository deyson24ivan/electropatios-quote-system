CREATE DATABASE IF NOT EXISTS electropatios_automation
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE electropatios_automation;

-- Tabla principal: cada fila es una solicitud de cotizacion o asesoria.
CREATE TABLE IF NOT EXISTS quote_requests (
  id CHAR(36) PRIMARY KEY,
  duplicate_key VARCHAR(255) NOT NULL UNIQUE,
  full_name VARCHAR(160) NOT NULL,
  email VARCHAR(190) NOT NULL,
  phone VARCHAR(40) NOT NULL,
  customer_type VARCHAR(80) NOT NULL DEFAULT 'persona',
  company_name VARCHAR(180) NULL,
  request_type ENUM('quote', 'question', 'advisor') NOT NULL DEFAULT 'quote',
  product_category VARCHAR(80) NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 0,
  unit VARCHAR(40) NOT NULL DEFAULT 'unidad',
  budget_cop BIGINT UNSIGNED NOT NULL DEFAULT 0,
  urgency VARCHAR(60) NOT NULL DEFAULT 'this_week',
  delivery_city VARCHAR(120) NOT NULL DEFAULT 'Cucuta',
  source VARCHAR(100) NOT NULL DEFAULT 'electropatios_web',
  notes TEXT,
  items_json JSON NULL,
  priority ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'low',
  score TINYINT UNSIGNED NOT NULL DEFAULT 0,
  status ENUM('new', 'pending_review', 'qualified', 'quoted', 'won', 'lost')
    NOT NULL DEFAULT 'new',
  priority_reason VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_quotes_email (email),
  INDEX idx_quotes_phone (phone),
  INDEX idx_quotes_product_category (product_category),
  INDEX idx_quotes_priority_status (priority, status),
  INDEX idx_quotes_created_at (created_at)
);

-- Tabla de eventos: sirve para guardar cambios importantes sobre una solicitud.
CREATE TABLE IF NOT EXISTS quote_events (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  quote_id CHAR(36) NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  event_payload JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_quote_events_quote
    FOREIGN KEY (quote_id) REFERENCES quote_requests(id)
    ON DELETE CASCADE,
  INDEX idx_quote_events_quote_id (quote_id),
  INDEX idx_quote_events_type (event_type)
);

-- Tabla comercial: cada cotizacion se convierte en un lead que puede ir a Sheets o CRM.
CREATE TABLE IF NOT EXISTS lead_records (
  id CHAR(36) PRIMARY KEY,
  duplicate_key VARCHAR(255) NOT NULL UNIQUE,
  quote_id CHAR(36) NOT NULL,
  full_name VARCHAR(160) NOT NULL,
  first_name VARCHAR(80) NULL,
  last_name VARCHAR(120) NULL,
  email VARCHAR(190) NOT NULL,
  phone VARCHAR(40) NOT NULL,
  company_name VARCHAR(180) NULL,
  customer_type VARCHAR(80) NOT NULL DEFAULT 'persona',
  delivery_city VARCHAR(120) NOT NULL DEFAULT 'Cucuta',
  product_category VARCHAR(80) NOT NULL,
  products_summary TEXT,
  quantity INT UNSIGNED NOT NULL DEFAULT 0,
  urgency VARCHAR(60) NOT NULL DEFAULT 'this_week',
  priority ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'low',
  lead_score TINYINT UNSIGNED NOT NULL DEFAULT 0,
  pipeline_stage VARCHAR(80) NOT NULL DEFAULT 'nutrir_o_asesorar',
  follow_up_status VARCHAR(80) NOT NULL DEFAULT 'pendiente',
  task_due_at TIMESTAMP NULL,
  estimated_value_cop BIGINT UNSIGNED NOT NULL DEFAULT 0,
  source VARCHAR(100) NOT NULL DEFAULT 'electropatios_web',
  notes TEXT,
  tags_json JSON NULL,
  sheet_row_json JSON NULL,
  ghl_payloads_json JSON NULL,
  advisor_message TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_lead_records_quote
    FOREIGN KEY (quote_id) REFERENCES quote_requests(id)
    ON DELETE CASCADE,
  INDEX idx_leads_quote_id (quote_id),
  INDEX idx_leads_email (email),
  INDEX idx_leads_phone (phone),
  INDEX idx_leads_priority_stage (priority, pipeline_stage),
  INDEX idx_leads_created_at (created_at)
);

-- Notificaciones preparadas para el asesor. Luego esto puede reemplazarse por email, WhatsApp o GoHighLevel task.
CREATE TABLE IF NOT EXISTS advisor_notifications (
  id CHAR(36) PRIMARY KEY,
  lead_id CHAR(36) NULL,
  quote_id CHAR(36) NULL,
  channel VARCHAR(80) NOT NULL DEFAULT 'advisor_inbox',
  priority ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'medium',
  message TEXT NOT NULL,
  status VARCHAR(80) NOT NULL DEFAULT 'prepared',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_notifications_lead_id (lead_id),
  INDEX idx_notifications_quote_id (quote_id),
  INDEX idx_notifications_status (status)
);

-- Intentos de CRM: en modo seguro guardamos que se mandaria a GoHighLevel.
CREATE TABLE IF NOT EXISTS crm_sync_attempts (
  id CHAR(36) PRIMARY KEY,
  lead_id CHAR(36) NULL,
  quote_id CHAR(36) NULL,
  provider VARCHAR(80) NOT NULL DEFAULT 'gohighlevel',
  mode VARCHAR(80) NOT NULL DEFAULT 'safe_mode',
  status VARCHAR(80) NOT NULL DEFAULT 'dry_run_prepared',
  will_send_to_crm BOOLEAN NOT NULL DEFAULT FALSE,
  contact_request_json JSON NULL,
  opportunity_request_json JSON NULL,
  missing_config_json JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_crm_syncs_lead_id (lead_id),
  INDEX idx_crm_syncs_quote_id (quote_id),
  INDEX idx_crm_syncs_status (status),
  INDEX idx_crm_syncs_created_at (created_at)
);

-- Analisis de IA en modo seguro: clasifica y prepara respuesta sin llamar a un modelo externo.
CREATE TABLE IF NOT EXISTS ai_safe_analyses (
  id CHAR(36) PRIMARY KEY,
  lead_id CHAR(36) NULL,
  quote_id CHAR(36) NULL,
  mode VARCHAR(80) NOT NULL DEFAULT 'safe_mode',
  status VARCHAR(80) NOT NULL DEFAULT 'safe_reply_prepared',
  will_call_ai_model BOOLEAN NOT NULL DEFAULT FALSE,
  intent VARCHAR(80) NOT NULL DEFAULT 'unknown',
  category VARCHAR(80) NOT NULL DEFAULT 'otros',
  confidence VARCHAR(40) NOT NULL DEFAULT 'low',
  handoff_required BOOLEAN NOT NULL DEFAULT TRUE,
  handoff_reason VARCHAR(120) NOT NULL DEFAULT 'baja_confianza',
  safe_reply TEXT,
  guardrails_json JSON NULL,
  suggested_tags_json JSON NULL,
  prompt_pack_json JSON NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ai_lead_id (lead_id),
  INDEX idx_ai_quote_id (quote_id),
  INDEX idx_ai_intent (intent),
  INDEX idx_ai_handoff (handoff_required),
  INDEX idx_ai_created_at (created_at)
);

-- Llamadas en modo seguro: simula un agente telefonico sin llamar proveedor de voz real.
CREATE TABLE IF NOT EXISTS voice_call_intakes (
  id CHAR(36) PRIMARY KEY,
  mode VARCHAR(80) NOT NULL DEFAULT 'safe_mode',
  status VARCHAR(80) NOT NULL DEFAULT 'voice_reply_prepared',
  provider VARCHAR(80) NOT NULL DEFAULT 'local_simulator',
  will_call_voice_provider BOOLEAN NOT NULL DEFAULT FALSE,
  will_call_ai_model BOOLEAN NOT NULL DEFAULT FALSE,
  caller_name VARCHAR(160) NULL,
  phone VARCHAR(40) NULL,
  email VARCHAR(190) NULL,
  delivery_city VARCHAR(120) NULL,
  transcript TEXT,
  intent VARCHAR(80) NOT NULL DEFAULT 'unknown',
  product_category VARCHAR(80) NOT NULL DEFAULT 'otros',
  quantity INT UNSIGNED NOT NULL DEFAULT 0,
  unit VARCHAR(40) NOT NULL DEFAULT 'unidad',
  urgency VARCHAR(60) NOT NULL DEFAULT 'esta_semana',
  priority ENUM('high', 'medium', 'low') NOT NULL DEFAULT 'low',
  confidence VARCHAR(40) NOT NULL DEFAULT 'low',
  handoff_required BOOLEAN NOT NULL DEFAULT TRUE,
  handoff_reason VARCHAR(120) NOT NULL DEFAULT 'faltan_datos',
  safe_voice_reply TEXT,
  guardrails_json JSON NULL,
  next_questions_json JSON NULL,
  voice_lead_draft_json JSON NULL,
  advisor_brief TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_voice_phone (phone),
  INDEX idx_voice_intent (intent),
  INDEX idx_voice_priority (priority),
  INDEX idx_voice_handoff (handoff_required),
  INDEX idx_voice_created_at (created_at)
);

-- Tabla de errores: ayuda a revisar fallos de automatizaciones.
CREATE TABLE IF NOT EXISTS automation_errors (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  quote_id CHAR(36) NULL,
  source VARCHAR(80) NOT NULL,
  error_message TEXT NOT NULL,
  payload JSON NULL,
  resolved BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_automation_errors_resolved (resolved),
  INDEX idx_automation_errors_created_at (created_at)
);
