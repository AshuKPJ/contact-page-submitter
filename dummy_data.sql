-- Complete dummy data for Contact Page Submitter development
-- Run this script in your PostgreSQL database

-- First, create subscription plans
INSERT INTO subscription_plans (id, name, description, max_websites, max_submissions_per_day, max_campaigns, price, currency, features, is_active, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', 'Free Plan', 'Basic plan for testing', 5, 50, 2, 0.00, 'USD', '{"basic_features": true, "email_support": false}', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440002', 'Pro Plan', 'Professional plan with advanced features', 50, 500, 10, 29.99, 'USD', '{"advanced_features": true, "email_support": true, "priority_support": false}', true, NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440003', 'Enterprise', 'Enterprise plan with unlimited access', -1, 5000, -1, 99.99, 'USD', '{"unlimited": true, "priority_support": true, "custom_integrations": true}', true, NOW(), NOW());

-- Create dummy users
INSERT INTO users (id, email, password_hash, first_name, last_name, role, is_active, is_verified, plan_id, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440010', 'john.doe@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiPMOr.Mk1u2', 'John', 'Doe', 'user', true, true, '550e8400-e29b-41d4-a716-446655440002', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440011', 'jane.smith@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiPMOr.Mk1u2', 'Jane', 'Smith', 'admin', true, true, '550e8400-e29b-41d4-a716-446655440003', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440012', 'demo@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiPMOr.Mk1u2', 'Demo', 'User', 'user', true, true, '550e8400-e29b-41d4-a716-446655440001', NOW(), NOW());

-- Create user subscriptions
INSERT INTO subscriptions (id, user_id, plan_id, status, start_date, end_date, external_id, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440002', 'active', NOW() - INTERVAL '30 days', NOW() + INTERVAL '30 days', 'stripe_sub_12345', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440003', 'active', NOW() - INTERVAL '60 days', NOW() + INTERVAL '60 days', 'stripe_sub_67890', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440001', 'active', NOW() - INTERVAL '7 days', NOW() + INTERVAL '23 days', null, NOW(), NOW());

-- Create user profiles
INSERT INTO user_profiles (id, user_id, first_name, last_name, email, phone_number, company_name, job_title, website_url, linkedin_url, industry, city, state, zip_code, country, region, timezone, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440030', '550e8400-e29b-41d4-a716-446655440010', 'John', 'Doe', 'john.doe@example.com', '+1-555-0123', 'TechCorp Inc.', 'Marketing Manager', 'https://techcorp.example.com', 'https://linkedin.com/in/johndoe', 'Technology', 'San Francisco', 'CA', '94105', 'USA', 'North America', 'America/Los_Angeles', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440031', '550e8400-e29b-41d4-a716-446655440011', 'Jane', 'Smith', 'jane.smith@example.com', '+1-555-0124', 'Digital Solutions LLC', 'CEO', 'https://digitalsolutions.example.com', 'https://linkedin.com/in/janesmith', 'Digital Marketing', 'New York', 'NY', '10001', 'USA', 'North America', 'America/New_York', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440032', '550e8400-e29b-41d4-a716-446655440012', 'Demo', 'User', 'demo@example.com', '+1-555-0125', 'Demo Company', 'Sales Representative', 'https://democompany.example.com', null, 'Sales', 'Austin', 'TX', '73301', 'USA', 'North America', 'America/Chicago', NOW(), NOW());

-- Create user contact profiles
INSERT INTO user_contact_profiles (id, user_id, first_name, last_name, company_name, job_title, email, phone_number, website_url, subject, referral_source, message, preferred_contact, city, state, industry, best_time_to_contact, budget_range, product_interest, is_existing_customer, country, language, timezone, linkedin_url, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440040', '550e8400-e29b-41d4-a716-446655440010', 'John', 'Doe', 'TechCorp Inc.', 'Marketing Manager', 'john.doe@techcorp.com', '+1-555-0123', 'https://techcorp.example.com', 'Partnership Inquiry', 'Google Search', 'Hi, I am interested in exploring partnership opportunities with your company. We have a complementary service that could benefit both our customer bases.', 'email', 'San Francisco', 'CA', 'Technology', 'Business Hours', '$10k-$50k', 'Enterprise Solutions', false, 'USA', 'English', 'America/Los_Angeles', 'https://linkedin.com/in/johndoe', NOW(), NOW()),
    ('550e8400-e29b-41d4-a716-446655440041', '550e8400-e29b-41d4-a716-446655440011', 'Jane', 'Smith', 'Digital Solutions LLC', 'CEO', 'jane.smith@digitalsolutions.com', '+1-555-0124', 'https://digitalsolutions.example.com', 'Service Inquiry', 'LinkedIn', 'Hello, we are looking for automated contact form submission services for our clients. Could you provide more information about your enterprise packages?', 'phone', 'New York', 'NY', 'Digital Marketing', 'Afternoon', '$50k+', 'Enterprise Package', false, 'USA', 'English', 'America/New_York', 'https://linkedin.com/in/janesmith', NOW(), NOW());

-- Create campaigns
INSERT INTO campaigns (id, user_id, name, message, status, total_urls, submitted_count, failed_count, started_at, completed_at, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', 'Q4 Partnership Outreach', 'Hi, I am John from TechCorp. We are interested in exploring partnership opportunities with your company.', 'active', 25, 18, 2, NOW() - INTERVAL '5 days', null, NOW() - INTERVAL '7 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440051', '550e8400-e29b-41d4-a716-446655440010', 'Product Launch Campaign', 'Hello! We are excited to announce our new product that could benefit your business.', 'completed', 15, 15, 0, NOW() - INTERVAL '30 days', NOW() - INTERVAL '25 days', NOW() - INTERVAL '35 days', NOW() - INTERVAL '25 days'),
    ('550e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440011', 'Enterprise Client Acquisition', 'Greetings from Digital Solutions LLC. We would like to discuss how our services can help your business grow.', 'active', 50, 35, 5, NOW() - INTERVAL '10 days', null, NOW() - INTERVAL '12 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440053', '550e8400-e29b-41d4-a716-446655440012', 'Demo Campaign Test', 'This is a test message for demonstration purposes.', 'draft', 5, 0, 0, null, null, NOW() - INTERVAL '2 days', NOW());

-- Create websites
INSERT INTO websites (id, campaign_id, user_id, domain, contact_url, form_detected, form_type, form_labels, form_field_count, has_captcha, captcha_type, status, failure_reason, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440060', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', 'example.com', 'https://example.com/contact', true, 'standard_contact', '["name", "email", "company", "message"]', 4, false, null, 'active', null, NOW() - INTERVAL '5 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440061', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', 'testsite.org', 'https://testsite.org/contact-us', true, 'advanced_contact', '["first_name", "last_name", "email", "phone", "company", "subject", "message"]', 7, true, 'recaptcha', 'active', null, NOW() - INTERVAL '4 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440062', '550e8400-e29b-41d4-a716-446655440051', '550e8400-e29b-41d4-a716-446655440010', 'demo-company.net', 'https://demo-company.net/get-in-touch', true, 'simple_form', '["name", "email", "inquiry"]', 3, false, null, 'completed', null, NOW() - INTERVAL '30 days', NOW() - INTERVAL '25 days'),
    ('550e8400-e29b-41d4-a716-446655440063', '550e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440011', 'bigcorp.com', 'https://bigcorp.com/contact', true, 'enterprise_form', '["first_name", "last_name", "company", "title", "email", "phone", "budget", "message"]', 8, true, 'hcaptcha', 'active', null, NOW() - INTERVAL '8 days', NOW());

-- Create submissions
INSERT INTO submissions (id, campaign_id, user_id, website_id, url, contact_method, email_extracted, status, success, response_status, error_message, form_fields_sent, captcha_encountered, captcha_solved, retry_count, created_at, updated_at, submitted_at, processed_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440060', 'https://example.com/contact', 'form_submission', 'contact@example.com', 'success', true, 200, null, '{"name": "John Doe", "email": "john.doe@techcorp.com", "company": "TechCorp Inc.", "message": "Partnership inquiry"}', false, false, 0, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440071', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440061', 'https://testsite.org/contact-us', 'form_submission', 'info@testsite.org', 'success', true, 200, null, '{"first_name": "John", "last_name": "Doe", "email": "john.doe@techcorp.com", "phone": "+1-555-0123", "company": "TechCorp Inc.", "subject": "Partnership", "message": "Interested in collaboration"}', true, true, 0, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440072', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440062', 'https://demo-company.net/get-in-touch', 'form_submission', null, 'failed', false, 403, 'Rate limit exceeded', '{"name": "John Doe", "email": "john.doe@techcorp.com", "inquiry": "Product demo request"}', false, false, 2, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440073', '550e8400-e29b-41d4-a716-446655440052', '550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440063', 'https://bigcorp.com/contact', 'form_submission', 'enterprise@bigcorp.com', 'pending', false, null, null, '{"first_name": "Jane", "last_name": "Smith", "company": "Digital Solutions LLC", "title": "CEO", "email": "jane.smith@digitalsolutions.com", "phone": "+1-555-0124", "budget": "$50k+", "message": "Enterprise solution inquiry"}', true, false, 1, NOW() - INTERVAL '1 hour', NOW() - INTERVAL '1 hour', null, null);

-- Create submission logs
INSERT INTO submission_logs (id, campaign_id, submission_id, user_id, website_id, target_url, action, details, status, timestamp)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440080', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440060', 'https://example.com/contact', 'form_submission_started', 'Initiated contact form submission', 'success', NOW() - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440081', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440060', 'https://example.com/contact', 'form_fields_populated', 'Successfully filled all form fields', 'success', NOW() - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440082', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440070', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440060', 'https://example.com/contact', 'form_submitted', 'Form submitted successfully with 200 response', 'success', NOW() - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440083', '550e8400-e29b-41d4-a716-446655440050', '550e8400-e29b-41d4-a716-446655440072', '550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440062', 'https://demo-company.net/get-in-touch', 'form_submission_failed', 'Rate limit exceeded after 2 retries', 'failed', NOW() - INTERVAL '1 day');

-- Create captcha logs
INSERT INTO captcha_logs (id, submission_id, captcha_type, solved, solution_time, error_message, timestamp)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440090', '550e8400-e29b-41d4-a716-446655440071', 'recaptcha', true, 12, null, NOW() - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440091', '550e8400-e29b-41d4-a716-446655440073', 'hcaptcha', false, null, 'Captcha service timeout after 30 seconds', NOW() - INTERVAL '1 hour');

-- Create system logs
INSERT INTO system_logs (id, user_id, action, details, timestamp)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440100', '550e8400-e29b-41d4-a716-446655440010', 'user_login', 'User logged in successfully', NOW() - INTERVAL '2 hours'),
    ('550e8400-e29b-41d4-a716-446655440101', '550e8400-e29b-41d4-a716-446655440010', 'campaign_created', 'Created new campaign: Q4 Partnership Outreach', NOW() - INTERVAL '7 days'),
    ('550e8400-e29b-41d4-a716-446655440102', '550e8400-e29b-41d4-a716-446655440011', 'user_login', 'Admin user logged in successfully', NOW() - INTERVAL '1 hour'),
    ('550e8400-e29b-41d4-a716-446655440103', '550e8400-e29b-41d4-a716-446655440011', 'system_maintenance', 'Performed routine system maintenance', NOW() - INTERVAL '6 hours'),
    ('550e8400-e29b-41d4-a716-446655440104', '550e8400-e29b-41d4-a716-446655440012', 'user_registered', 'New demo user account created', NOW() - INTERVAL '7 days');

-- Create application logs
INSERT INTO logs (id, user_id, message, level, timestamp)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440110', '550e8400-e29b-41d4-a716-446655440010', 'Form submission completed successfully for example.com', 'INFO', NOW() - INTERVAL '3 days'),
    ('550e8400-e29b-41d4-a716-446655440111', '550e8400-e29b-41d4-a716-446655440010', 'Captcha encountered on testsite.org, solving...', 'WARNING', NOW() - INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440112', '550e8400-e29b-41d4-a716-446655440010', 'Rate limit reached for demo-company.net, retrying in 1 hour', 'ERROR', NOW() - INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440113', '550e8400-e29b-41d4-a716-446655440011', 'Enterprise campaign started with 50 target URLs', 'INFO', NOW() - INTERVAL '10 days'),
    ('550e8400-e29b-41d4-a716-446655440114', null, 'System startup completed successfully', 'INFO', NOW() - INTERVAL '12 hours');

-- Create user settings
INSERT INTO settings (id, user_id, key, value, created_at, updated_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440120', '550e8400-e29b-41d4-a716-446655440010', 'email_notifications', 'true', NOW() - INTERVAL '7 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440121', '550e8400-e29b-41d4-a716-446655440010', 'submission_delay', '2', NOW() - INTERVAL '7 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440122', '550e8400-e29b-41d4-a716-446655440010', 'max_retries', '3', NOW() - INTERVAL '7 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440123', '550e8400-e29b-41d4-a716-446655440011', 'admin_notifications', 'true', NOW() - INTERVAL '60 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440124', '550e8400-e29b-41d4-a716-446655440011', 'system_monitoring', 'enabled', NOW() - INTERVAL '60 days', NOW()),
    ('550e8400-e29b-41d4-a716-446655440125', '550e8400-e29b-41d4-a716-446655440012', 'demo_mode', 'true', NOW() - INTERVAL '7 days', NOW());

-- Display summary
SELECT 'Data insertion completed! Summary:' as status;
SELECT 
    'subscription_plans' as table_name, COUNT(*) as records_created FROM subscription_plans
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'subscriptions', COUNT(*) FROM subscriptions  
UNION ALL SELECT 'user_profiles', COUNT(*) FROM user_profiles
UNION ALL SELECT 'user_contact_profiles', COUNT(*) FROM user_contact_profiles
UNION ALL SELECT 'campaigns', COUNT(*) FROM campaigns
UNION ALL SELECT 'websites', COUNT(*) FROM websites
UNION ALL SELECT 'submissions', COUNT(*) FROM submissions
UNION ALL SELECT 'submission_logs', COUNT(*) FROM submission_logs
UNION ALL SELECT 'captcha_logs', COUNT(*) FROM captcha_logs
UNION ALL SELECT 'system_logs', COUNT(*) FROM system_logs
UNION ALL SELECT 'logs', COUNT(*) FROM logs
UNION ALL SELECT 'settings', COUNT(*) FROM settings;