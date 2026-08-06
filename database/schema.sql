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

