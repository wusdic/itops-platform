-- Migration: 012_create_knowledge_base_tables
-- Creates knowledge base tables needed for KB module (fault cases, categories, tags, SOP documents)

CREATE TABLE IF NOT EXISTS kb_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE,
    parent_id INT,
    doc_type VARCHAR(20) DEFAULT 'sop',  -- 'sop', 'fault_case', 'general'
    icon VARCHAR(50),
    description TEXT,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_doc_type (doc_type),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS kb_fault_cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_no VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,

    -- Fault basic info
    fault_level ENUM('P1', 'P2', 'P3', 'P4') DEFAULT 'P3',
    fault_status ENUM('open', 'investigating', 'resolved', 'closed') DEFAULT 'open',
    fault_category VARCHAR(100),
    symptom TEXT,
    root_cause TEXT,

    -- Impact scope
    affected_systems JSON,
    affected_services JSON,
    user_impact VARCHAR(20) DEFAULT 'none',
    business_impact VARCHAR(50),
    duration INT COMMENT 'Duration in minutes',
    outage_time INT COMMENT 'Outage time in minutes',

    -- Resolution
    solution TEXT,
    workaround TEXT,
    prevention TEXT,

    -- Lessons
    lessons_learned TEXT,
    improvement TEXT,
    related_docs JSON,
    related_cases JSON,

    -- Metadata
    tags VARCHAR(500),
    category_id INT,
    occurrence_time DATETIME,
    resolution_time DATETIME,
    author VARCHAR(100),
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    extra_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    INDEX idx_case_no (case_no),
    INDEX idx_fault_level (fault_level),
    INDEX idx_fault_status (fault_status),
    INDEX idx_fault_category (fault_category),
    INDEX idx_category (category_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS kb_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS kb_document_chunks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_type VARCHAR(20) NOT NULL,  -- 'sop' or 'fault_case'
    document_id INT NOT NULL,
    fault_case_id INT,
    chunk_index INT,
    content TEXT,
    vector_embedding JSON,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_document (document_type, document_id),
    INDEX idx_fault_case (fault_case_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SOP documents table
CREATE TABLE IF NOT EXISTS kb_sop_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doc_no VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    category_id INT,
    version VARCHAR(20) DEFAULT '1.0',
    status ENUM('draft', 'pending_review', 'approved', 'archived') DEFAULT 'draft',
    author VARCHAR(100),
    approver VARCHAR(100),
    tags VARCHAR(500),
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_author (author)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SOP reviews table
CREATE TABLE IF NOT EXISTS kb_document_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_type VARCHAR(20) DEFAULT 'sop',
    document_id INT NOT NULL,
    review_type VARCHAR(20),  -- 'review' or 'approve'
    reviewer VARCHAR(100) NOT NULL,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_document (document_type, document_id),
    INDEX idx_reviewer (reviewer),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
