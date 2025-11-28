-- =============================================
-- Azure SQL Database Schema for Playwright Automation Metadata
-- =============================================

-- Drop tables if they exist (in reverse order due to foreign keys)
IF OBJECT_ID('dbo.PageElements', 'U') IS NOT NULL DROP TABLE dbo.PageElements;
IF OBJECT_ID('dbo.Pages', 'U') IS NOT NULL DROP TABLE dbo.Pages;
IF OBJECT_ID('dbo.Screenshots', 'U') IS NOT NULL DROP TABLE dbo.Screenshots;
IF OBJECT_ID('dbo.TestExecutions', 'U') IS NOT NULL DROP TABLE dbo.TestExecutions;

-- =============================================
-- Main Test Executions Table
-- =============================================
CREATE TABLE dbo.TestExecutions (
    -- Primary Key
    execution_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Test Identification
    test_id NVARCHAR(100) NOT NULL,
    
    -- Execution Status
    status NVARCHAR(20) NOT NULL CHECK (status IN ('success', 'failed', 'error', 'timeout')),
    
    -- Timing Information
    execution_time DECIMAL(10, 2) NOT NULL,
    steps_executed INT NOT NULL DEFAULT 0,
    executed_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Agent Output (Full execution log)
    agent_output NVARCHAR(MAX) NULL,
    
    -- Error Information
    error_message NVARCHAR(MAX) NULL,
    
    -- Metadata
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Indexes
    INDEX IX_TestExecutions_TestId (test_id),
    INDEX IX_TestExecutions_Status (status),
    INDEX IX_TestExecutions_ExecutedAt (executed_at DESC)
);

-- =============================================
-- Screenshots Table
-- =============================================
CREATE TABLE dbo.Screenshots (
    -- Primary Key
    screenshot_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Key
    execution_id INT NOT NULL,
    
    -- Screenshot Information
    filename NVARCHAR(500) NOT NULL,
    file_path NVARCHAR(1000) NULL,
    step_number INT NULL,
    description NVARCHAR(500) NULL,
    
    -- Metadata
    captured_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    file_size_kb INT NULL,
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Screenshots_TestExecutions 
        FOREIGN KEY (execution_id) REFERENCES dbo.TestExecutions(execution_id)
        ON DELETE CASCADE,
    
    -- Indexes
    INDEX IX_Screenshots_ExecutionId (execution_id)
);

-- =============================================
-- Pages Table (Nodes in the graph)
-- =============================================
CREATE TABLE dbo.Pages (
    -- Primary Key
    page_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Key
    execution_id INT NOT NULL,
    
    -- Page Identification
    page_node_id NVARCHAR(100) NOT NULL, -- e.g., "page_1"
    page_label NVARCHAR(500) NOT NULL,
    
    -- Graph Position
    x_position INT NULL,
    y_position INT NULL,
    
    -- Page Metadata
    url NVARCHAR(2000) NOT NULL,
    title NVARCHAR(500) NULL,
    
    -- Additional Metadata
    page_order INT NULL, -- Order in which page was visited
    visit_count INT NULL DEFAULT 1,
    
    -- Timestamps
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Pages_TestExecutions 
        FOREIGN KEY (execution_id) REFERENCES dbo.TestExecutions(execution_id)
        ON DELETE CASCADE,
    
    -- Indexes
    INDEX IX_Pages_ExecutionId (execution_id),
    INDEX IX_Pages_NodeId (page_node_id),
    INDEX IX_Pages_URL (url(450))
);

-- =============================================
-- Page Elements Table (Key elements on each page)
-- =============================================
CREATE TABLE dbo.PageElements (
    -- Primary Key
    element_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Key
    page_id INT NOT NULL,
    
    -- Element Information
    element_type NVARCHAR(100) NULL, -- e.g., "button", "input", "link"
    element_label NVARCHAR(500) NULL,
    element_selector NVARCHAR(1000) NULL, -- CSS selector
    element_xpath NVARCHAR(2000) NULL,
    
    -- Element Attributes
    element_id_attr NVARCHAR(200) NULL, -- HTML id attribute
    element_class NVARCHAR(500) NULL, -- HTML class attribute
    element_name NVARCHAR(200) NULL, -- HTML name attribute
    
    -- Element Text/Value
    text_content NVARCHAR(MAX) NULL,
    placeholder NVARCHAR(500) NULL,
    
    -- Element State
    is_visible BIT NULL DEFAULT 1,
    is_enabled BIT NULL DEFAULT 1,
    is_required BIT NULL DEFAULT 0,
    
    -- Position/Size
    x_position INT NULL,
    y_position INT NULL,
    width INT NULL,
    height INT NULL,
    
    -- Interaction Information
    was_clicked BIT NULL DEFAULT 0,
    was_typed_into BIT NULL DEFAULT 0,
    interaction_count INT NULL DEFAULT 0,
    
    -- Metadata
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Foreign Key Constraint
    CONSTRAINT FK_PageElements_Pages 
        FOREIGN KEY (page_id) REFERENCES dbo.Pages(page_id)
        ON DELETE CASCADE,
    
    -- Indexes
    INDEX IX_PageElements_PageId (page_id),
    INDEX IX_PageElements_Type (element_type),
    INDEX IX_PageElements_Selector (element_selector(450))
);

-- =============================================
-- Page Edges Table (Navigation relationships)
-- =============================================
IF OBJECT_ID('dbo.PageEdges', 'U') IS NOT NULL DROP TABLE dbo.PageEdges;

CREATE TABLE dbo.PageEdges (
    -- Primary Key
    edge_id INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Foreign Key
    execution_id INT NOT NULL,
    
    -- Edge Information
    edge_node_id NVARCHAR(100) NOT NULL, -- e.g., "edge_1"
    source_page_node_id NVARCHAR(100) NOT NULL, -- References page_node_id
    target_page_node_id NVARCHAR(100) NOT NULL, -- References page_node_id
    edge_label NVARCHAR(500) NULL,
    
    -- Edge Type
    edge_type NVARCHAR(50) NULL DEFAULT 'navigation', -- navigation, click, form_submit, etc.
    
    -- Interaction Details
    action_performed NVARCHAR(500) NULL,
    element_clicked NVARCHAR(500) NULL,
    
    -- Metadata
    created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    
    -- Foreign Key Constraint
    CONSTRAINT FK_PageEdges_TestExecutions 
        FOREIGN KEY (execution_id) REFERENCES dbo.TestExecutions(execution_id)
        ON DELETE CASCADE,
    
    -- Indexes
    INDEX IX_PageEdges_ExecutionId (execution_id),
    INDEX IX_PageEdges_Source (source_page_node_id),
    INDEX IX_PageEdges_Target (target_page_node_id)
);

-- =============================================
-- Create Views for Easy Querying
-- =============================================

-- View: Complete Test Execution Summary
CREATE OR ALTER VIEW vw_TestExecutionSummary AS
SELECT 
    te.execution_id,
    te.test_id,
    te.status,
    te.execution_time,
    te.steps_executed,
    te.executed_at,
    te.error_message,
    COUNT(DISTINCT p.page_id) as total_pages,
    COUNT(DISTINCT s.screenshot_id) as total_screenshots,
    COUNT(DISTINCT pe.element_id) as total_elements
FROM dbo.TestExecutions te
LEFT JOIN dbo.Pages p ON te.execution_id = p.execution_id
LEFT JOIN dbo.Screenshots s ON te.execution_id = s.execution_id
LEFT JOIN dbo.PageElements pe ON p.page_id = pe.page_id
GROUP BY 
    te.execution_id,
    te.test_id,
    te.status,
    te.execution_time,
    te.steps_executed,
    te.executed_at,
    te.error_message;
GO

-- View: Page Details with Elements
CREATE OR ALTER VIEW vw_PageDetails AS
SELECT 
    p.page_id,
    p.execution_id,
    p.page_node_id,
    p.page_label,
    p.url,
    p.title,
    p.x_position,
    p.y_position,
    COUNT(pe.element_id) as element_count
FROM dbo.Pages p
LEFT JOIN dbo.PageElements pe ON p.page_id = pe.page_id
GROUP BY 
    p.page_id,
    p.execution_id,
    p.page_node_id,
    p.page_label,
    p.url,
    p.title,
    p.x_position,
    p.y_position;
GO

-- =============================================
-- Create Stored Procedures
-- =============================================

-- Procedure: Get Test Execution by Test ID
CREATE OR ALTER PROCEDURE sp_GetTestExecutionByTestId
    @test_id NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT *
    FROM vw_TestExecutionSummary
    WHERE test_id = @test_id
    ORDER BY executed_at DESC;
END;
GO

-- Procedure: Get Pages for Execution
CREATE OR ALTER PROCEDURE sp_GetPagesForExecution
    @execution_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT *
    FROM vw_PageDetails
    WHERE execution_id = @execution_id
    ORDER BY page_order, page_id;
END;
GO

-- Procedure: Get Page Elements
CREATE OR ALTER PROCEDURE sp_GetPageElements
    @page_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT *
    FROM dbo.PageElements
    WHERE page_id = @page_id
    ORDER BY element_type, element_label;
END;
GO

-- =============================================
-- Grant Permissions (adjust as needed)
-- =============================================
-- GRANT SELECT, INSERT, UPDATE ON dbo.TestExecutions TO [YourAppUser];
-- GRANT SELECT, INSERT, UPDATE ON dbo.Pages TO [YourAppUser];
-- GRANT SELECT, INSERT, UPDATE ON dbo.PageElements TO [YourAppUser];
-- GRANT SELECT, INSERT, UPDATE ON dbo.Screenshots TO [YourAppUser];
-- GRANT SELECT, INSERT, UPDATE ON dbo.PageEdges TO [YourAppUser];

-- =============================================
-- Sample Queries
-- =============================================

-- Get all test executions with summary
-- SELECT * FROM vw_TestExecutionSummary ORDER BY executed_at DESC;

-- Get all pages for a specific execution
-- SELECT * FROM vw_PageDetails WHERE execution_id = 1;

-- Get all elements for a specific page
-- SELECT * FROM dbo.PageElements WHERE page_id = 1;

-- Get execution success rate
-- SELECT 
--     status,
--     COUNT(*) as count,
--     CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as percentage
-- FROM dbo.TestExecutions
-- GROUP BY status;

PRINT 'Database schema created successfully!';
