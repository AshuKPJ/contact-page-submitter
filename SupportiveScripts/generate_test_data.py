#!/usr/bin/env python3
"""
Test Data Generator for Your Exact Database Schema
Matches the provided table structure exactly
"""

import uuid
import hashlib
import secrets
import random
from datetime import datetime, timedelta
from typing import List, Dict
import json

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("Note: bcrypt not installed. Using SHA256 instead.")


class TestDataGenerator:
    """Generate test data matching exact database schema"""
    
    def __init__(self):
        self.generated_ids = {
            'users': [],
            'subscription_plans': [],
            'campaigns': [],
            'websites': [],
            'submissions': [],
            'user_profiles': [],
            'user_contact_profiles': []
        }
        
        # Test data templates
        self.first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'James', 'Lisa', 'Robert', 'Maria']
        self.last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        self.companies = ['TechCorp', 'DataSoft', 'WebSolutions', 'CloudNet', 'DigiMarketing', 'InfoSystems']
        self.industries = ['Technology', 'Finance', 'Healthcare', 'Education', 'Retail', 'Manufacturing']
        
    def generate_uuid(self) -> str:
        """Generate a UUID string"""
        return str(uuid.uuid4())
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            salt = secrets.token_hex(16)
            hash_value = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"sha256${salt}${hash_value}"
    
    def generate_subscription_plans(self) -> List[str]:
        """Generate subscription plan INSERT statements"""
        statements = []
        plan_data = [
            {
                'name': 'Free',
                'max_websites': 1,
                'max_submissions_per_day': 10,
                'price': 0.00,
                'features': {
                    'campaigns': 2,
                    'support': 'community',
                    'captcha_solving': False
                }
            },
            {
                'name': 'Basic',
                'max_websites': 5,
                'max_submissions_per_day': 100,
                'price': 9.99,
                'features': {
                    'campaigns': 10,
                    'support': 'email',
                    'captcha_solving': True,
                    'proxy_support': False
                }
            },
            {
                'name': 'Professional',
                'max_websites': 20,
                'max_submissions_per_day': 500,
                'price': 29.99,
                'features': {
                    'campaigns': 50,
                    'support': 'priority',
                    'captcha_solving': True,
                    'proxy_support': True
                }
            },
            {
                'name': 'Enterprise',
                'max_websites': 9999,  # Unlimited
                'max_submissions_per_day': 9999,  # Unlimited
                'price': 99.99,
                'features': {
                    'campaigns': 'unlimited',
                    'support': 'dedicated',
                    'captcha_solving': True,
                    'proxy_support': True,
                    'api_access': True
                }
            }
        ]
        
        for plan in plan_data:
            plan_id = self.generate_uuid()
            self.generated_ids['subscription_plans'].append(plan_id)
            
            stmt = f"""INSERT INTO subscription_plans (id, name, max_websites, max_submissions_per_day, price, features)
VALUES ('{plan_id}', '{plan['name']}', {plan['max_websites']}, {plan['max_submissions_per_day']}, {plan['price']}, '{json.dumps(plan['features'])}');"""
            statements.append(stmt)
        
        return statements
    
    def generate_users(self) -> List[str]:
        """Generate user INSERT statements"""
        statements = []
        roles = ['admin', 'moderator', 'user', 'user', 'user']
        
        for i in range(10):
            user_id = self.generate_uuid()
            self.generated_ids['users'].append(user_id)
            
            first_name = self.first_names[i % len(self.first_names)]
            last_name = self.last_names[i % len(self.last_names)]
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            password = f"{first_name}Pass{i}@2024"
            hashed_password = self.hash_password(password)
            role = roles[i % len(roles)]
            
            # Assign subscription plans
            if role == 'admin':
                plan_id = self.generated_ids['subscription_plans'][3]  # Enterprise
                subscription_status = 'active'
            elif role == 'moderator':
                plan_id = self.generated_ids['subscription_plans'][2]  # Professional
                subscription_status = 'active'
            elif i % 3 == 0:
                plan_id = self.generated_ids['subscription_plans'][0]  # Free
                subscription_status = 'free'
            else:
                plan_id = self.generated_ids['subscription_plans'][random.randint(1, 2)]
                subscription_status = random.choice(['active', 'trial', 'expired'])
            
            # Captcha credentials
            captcha_username = f"{first_name.lower()}_dbc_{i}"
            captcha_password = f"Captcha{i}@2024"
            captcha_password_hash = self.hash_password(captcha_password)
            
            subscription_start = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S') if subscription_status != 'free' else 'NULL'
            subscription_end = (datetime.now() + timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S') if subscription_status == 'active' else 'NULL'
            
            stmt = f"""INSERT INTO users (id, email, hashed_password, plan_id, subscription_status, subscription_start, subscription_end, role, first_name, last_name, captcha_username, captcha_password_hash, is_active)
VALUES ('{user_id}', '{email}', '{hashed_password}', '{plan_id}', '{subscription_status}', {f"'{subscription_start}'" if subscription_start != 'NULL' else 'NULL'}, {f"'{subscription_end}'" if subscription_end != 'NULL' else 'NULL'}, '{role}', '{first_name}', '{last_name}', '{captcha_username}', '{captcha_password_hash}', {i != 9});"""
            
            statements.append(stmt)
            
            # Print credentials for testing
            if i == 0:
                print("\n=== TEST USER CREDENTIALS ===")
                print(f"{'Email':<35} | {'Password':<20} | {'Role':<10} | {'Captcha User':<20} | {'Captcha Pass':<15}")
                print("-" * 110)
            print(f"{email:<35} | {password:<20} | {role:<10} | {captcha_username:<20} | {captcha_password:<15}")
        
        return statements
    
    def generate_user_profiles(self) -> List[str]:
        """Generate user_profiles INSERT statements"""
        statements = []
        
        for i, user_id in enumerate(self.generated_ids['users']):
            # user_profiles has integer id, not uuid
            profile_id = i + 1
            
            first_name = self.first_names[i % len(self.first_names)]
            last_name = self.last_names[i % len(self.last_names)]
            
            stmt = f"""INSERT INTO user_profiles (id, user_id, first_name, last_name, email, phone_number, company_name, job_title, website_url, industry, city, state, country, dbc_username, dbc_password, created_at)
VALUES ({profile_id}, '{user_id}', '{first_name}', '{last_name}', '{first_name.lower()}.{last_name.lower()}{i}@example.com', '+1{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}', '{self.companies[i % len(self.companies)]}', '{random.choice(["Manager", "Developer", "Analyst", "Director"])}', 'https://www.example{i}.com', '{self.industries[i % len(self.industries)]}', '{random.choice(["New York", "Los Angeles", "Chicago", "Houston"])}', '{random.choice(["NY", "CA", "IL", "TX"])}', 'United States', 'dbc_user_{i}', 'encrypted_pass_{i}', CURRENT_TIMESTAMP);"""
            
            statements.append(stmt)
            self.generated_ids['user_profiles'].append(profile_id)
        
        return statements
    
    def generate_user_contact_profiles(self) -> List[str]:
        """Generate user_contact_profiles INSERT statements"""
        statements = []
        
        for i, user_id in enumerate(self.generated_ids['users']):
            profile_id = self.generate_uuid()
            self.generated_ids['user_contact_profiles'].append(profile_id)
            
            first_name = self.first_names[i % len(self.first_names)]
            last_name = self.last_names[i % len(self.last_names)]
            
            stmt = f"""INSERT INTO user_contact_profiles (id, user_id, first_name, last_name, company_name, email, phone_number, city, state, country, preferred_contact, industry, budget_range)
VALUES ('{profile_id}', '{user_id}', '{first_name}', '{last_name}', '{self.companies[i % len(self.companies)]}', '{first_name.lower()}.{last_name.lower()}{i}@example.com', '+1{random.randint(200,999)}{random.randint(200,999)}{random.randint(1000,9999)}', '{random.choice(["New York", "Los Angeles", "Chicago"])}', '{random.choice(["NY", "CA", "IL"])}', 'United States', '{random.choice(["email", "phone"])}', '{self.industries[i % len(self.industries)]}', '{random.choice(["$1k-$5k", "$5k-$10k", "$10k-$50k", "$50k+"])}');"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_campaigns(self) -> List[str]:
        """Generate campaigns INSERT statements"""
        statements = []
        
        for i, user_id in enumerate(self.generated_ids['users']):
            # Each user gets 1-3 campaigns
            num_campaigns = random.randint(1, 3) if i < 8 else 0
            
            for j in range(num_campaigns):
                campaign_id = self.generate_uuid()
                self.generated_ids['campaigns'].append(campaign_id)
                
                name = f"Campaign {i}-{j} - {random.choice(['Lead Generation', 'Contact Forms', 'Survey Distribution', 'Newsletter Signup'])}"
                status = random.choice(['active', 'completed', 'paused', 'pending'])
                total_urls = random.randint(10, 500)
                submitted_count = random.randint(0, total_urls)
                failed_count = random.randint(0, 50)
                
                stmt = f"""INSERT INTO campaigns (id, user_id, name, csv_filename, started_at, status, message, use_captcha, total_urls, submitted_count, failed_count)
VALUES ('{campaign_id}', '{user_id}', '{name}', 'campaign_{i}_{j}.csv', CURRENT_TIMESTAMP - INTERVAL '{random.randint(1, 30)} days', '{status}', 'Test message for campaign', TRUE, {total_urls}, {submitted_count}, {failed_count});"""
                
                statements.append(stmt)
        
        return statements
    
    def generate_websites(self) -> List[str]:
        """Generate websites INSERT statements"""
        statements = []
        
        test_domains = [
            'www.techblog.com', 'www.salesforce.com', 'www.hubspot.com',
            'www.zendesk.com', 'www.intercom.com', 'www.drift.com',
            'www.mailchimp.com', 'www.constantcontact.com', 'www.sendinblue.com'
        ]
        
        for i, campaign_id in enumerate(self.generated_ids['campaigns'][:20]):  # First 20 campaigns
            website_id = self.generate_uuid()
            self.generated_ids['websites'].append(website_id)
            
            # Get user_id from campaign
            user_id = self.generated_ids['users'][i % len(self.generated_ids['users'])]
            
            domain = test_domains[i % len(test_domains)]
            contact_url = f"https://{domain}/contact"
            form_detected = random.choice([True, True, True, False])  # 75% have forms
            has_captcha = random.choice([True, False, False, False])  # 25% have captcha
            
            form_labels = "'{\"name\", \"email\", \"message\"}'::text[]" if form_detected else 'NULL'
            form_field_count = random.randint(3, 8) if form_detected else 0
            captcha_type = "'recaptcha'" if has_captcha else 'NULL'
            
            stmt = f"""INSERT INTO websites (id, campaign_id, domain, contact_url, form_detected, form_type, form_labels, form_field_count, has_captcha, captcha_type, status, user_id, requires_proxy)
VALUES ('{website_id}', '{campaign_id}', '{domain}', '{contact_url}', {form_detected}, {'\'contact\'' if form_detected else 'NULL'}, {form_labels}, {form_field_count}, {has_captcha}, {captcha_type}, 'active', '{user_id}', {random.choice([True, False])});"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_submissions(self) -> List[str]:
        """Generate submissions INSERT statements"""
        statements = []
        
        for website_id in self.generated_ids['websites'][:15]:  # First 15 websites
            num_submissions = random.randint(5, 20)
            
            for j in range(num_submissions):
                submission_id = self.generate_uuid()
                self.generated_ids['submissions'].append(submission_id)
                
                # Get a random campaign and user
                campaign_id = random.choice(self.generated_ids['campaigns'])
                user_id = random.choice(self.generated_ids['users'])
                
                success = random.choice([True, True, True, False])  # 75% success rate
                status = 'completed' if success else random.choice(['failed', 'pending', 'retry'])
                response_status = 200 if success else random.choice([404, 500, 403, 429])
                
                form_fields = {
                    'name': f'Test User {j}',
                    'email': f'testuser{j}@example.com',
                    'message': f'Test submission message number {j}',
                    'company': f'Test Company {j}'
                }
                
                captcha_encountered = random.choice([True, False, False, False])
                captcha_solved = captcha_encountered and random.choice([True, True, False])
                
                stmt = f"""INSERT INTO submissions (id, website_id, user_id, campaign_id, status, success, response_status, form_fields_sent, url, contact_method, email_extracted, captcha_encountered, captcha_solved, retry_count)
VALUES ('{submission_id}', '{website_id}', '{user_id}', '{campaign_id}', '{status}', {success}, {response_status}, '{json.dumps(form_fields)}', 'https://example.com/contact', 'form', 'contact@example.com', {captcha_encountered}, {captcha_solved}, {random.randint(0, 3)});"""
                
                statements.append(stmt)
        
        return statements
    
    def generate_submission_logs(self) -> List[str]:
        """Generate submission_logs INSERT statements"""
        statements = []
        
        for submission_id in self.generated_ids['submissions'][:50]:  # First 50 submissions
            log_id = self.generate_uuid()
            
            campaign_id = random.choice(self.generated_ids['campaigns'])
            user_id = random.choice(self.generated_ids['users'])
            website_id = random.choice(self.generated_ids['websites']) if self.generated_ids['websites'] else 'NULL'
            
            status = random.choice(['success', 'failed', 'pending', 'processing'])
            action = random.choice(['form_submitted', 'captcha_solved', 'proxy_used', 'retry_attempted'])
            
            stmt = f"""INSERT INTO submission_logs (id, campaign_id, target_url, status, details, user_id, website_id, submission_id, action)
VALUES ('{log_id}', '{campaign_id}', 'https://example.com/contact', '{status}', 'Processing submission log entry', '{user_id}', {f"'{website_id}'" if website_id != 'NULL' else 'NULL'}, '{submission_id}', '{action}');"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_captcha_logs(self) -> List[str]:
        """Generate captcha_logs INSERT statements"""
        statements = []
        
        for i in range(30):  # Generate 30 captcha log entries
            log_id = self.generate_uuid()
            
            submission_id = random.choice(self.generated_ids['submissions']) if self.generated_ids['submissions'] else None
            if not submission_id:
                continue
                
            captcha_type = random.choice(['recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'funcaptcha'])
            solved = random.choice([True, True, True, False])  # 75% success rate
            solve_time = random.uniform(1.5, 30.0) if solved else None
            dbc_balance = random.uniform(10.0, 100.0)
            
            stmt = f"""INSERT INTO captcha_logs (id, submission_id, captcha_type, solved, solve_time, dbc_balance, error, timestamp)
VALUES ('{log_id}', '{submission_id}', '{captcha_type}', {solved}, {solve_time if solve_time else 'NULL'}, {dbc_balance}, {f"'Failed to solve captcha'" if not solved else 'NULL'}, CURRENT_TIMESTAMP);"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_logs(self) -> List[str]:
        """Generate logs INSERT statements"""
        statements = []
        
        log_messages = [
            'Campaign started successfully',
            'Form submission completed',
            'Captcha encountered and solved',
            'Proxy connection established',
            'Website analysis completed',
            'CSV file uploaded',
            'Submission retry attempted'
        ]
        
        for i in range(50):  # Generate 50 log entries
            log_id = self.generate_uuid()
            
            user_id = random.choice(self.generated_ids['users']) if random.random() > 0.2 else 'NULL'
            campaign_id = random.choice(self.generated_ids['campaigns']) if self.generated_ids['campaigns'] and random.random() > 0.3 else 'NULL'
            website_id = random.choice(self.generated_ids['websites']) if self.generated_ids['websites'] and random.random() > 0.5 else 'NULL'
            
            level = random.choice(['INFO', 'WARNING', 'ERROR', 'DEBUG'])
            message = random.choice(log_messages)
            
            context = {
                'action': random.choice(['submit', 'analyze', 'retry', 'captcha_solve']),
                'user_agent': 'Mozilla/5.0',
                'ip': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}'
            }
            
            stmt = f"""INSERT INTO logs (id, user_id, campaign_id, website_id, level, message, context)
VALUES ('{log_id}', {f"'{user_id}'" if user_id != 'NULL' else 'NULL'}, {f"'{campaign_id}'" if campaign_id != 'NULL' else 'NULL'}, {f"'{website_id}'" if website_id != 'NULL' else 'NULL'}, '{level}', '{message}', '{json.dumps(context)}');"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_system_logs(self) -> List[str]:
        """Generate system_logs INSERT statements"""
        statements = []
        
        actions = [
            'user_login', 'user_logout', 'campaign_created', 'campaign_started',
            'submission_completed', 'api_key_generated', 'password_changed'
        ]
        
        for i in range(30):  # Generate 30 system log entries
            log_id = self.generate_uuid()
            
            user_id = random.choice(self.generated_ids['users']) if random.random() > 0.1 else 'NULL'
            action = random.choice(actions)
            ip_address = f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}'
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
            
            stmt = f"""INSERT INTO system_logs (id, user_id, action, details, ip_address, user_agent, timestamp)
VALUES ('{log_id}', {f"'{user_id}'" if user_id != 'NULL' else 'NULL'}, '{action}', 'System action performed', '{ip_address}', '{user_agent}', CURRENT_TIMESTAMP);"""
            
            statements.append(stmt)
        
        return statements
    
    def generate_settings(self) -> List[str]:
        """Generate settings INSERT statements"""
        statements = []
        
        # Global settings (no user_id)
        global_settings = [
            ('app_default_message', 'Hello, I am interested in your services. Please contact me.'),
            ('global_captcha_key', 'demo_captcha_api_key_123456'),
            ('default_proxy', 'http://proxy.example.com:8080')
        ]
        
        for setting in global_settings:
            setting_id = self.generate_uuid()
            stmt = f"""INSERT INTO settings (id, user_id, default_message_template, captcha_api_key, proxy_url, auto_submit)
VALUES ('{setting_id}', NULL, '{setting[1] if setting[0] == "app_default_message" else "NULL"}', '{setting[1] if setting[0] == "global_captcha_key" else "NULL"}', '{setting[1] if setting[0] == "default_proxy" else "NULL"}', FALSE);"""
            statements.append(stmt)
        
        # User-specific settings (first 3 users)
        for user_id in self.generated_ids['users'][:3]:
            setting_id = self.generate_uuid()
            stmt = f"""INSERT INTO settings (id, user_id, default_message_template, captcha_api_key, auto_submit)
VALUES ('{setting_id}', '{user_id}', 'Custom message template for user', 'user_specific_captcha_key_{random.randint(1000, 9999)}', {random.choice(['TRUE', 'FALSE'])});"""
            statements.append(stmt)
        
        return statements
    
    def generate_subscriptions(self) -> List[str]:
        """Generate subscriptions INSERT statements"""
        statements = []
        
        for user_id in self.generated_ids['users']:
            if random.random() > 0.3:  # 70% have subscriptions
                subscription_id = self.generate_uuid()
                plan_id = random.choice(self.generated_ids['subscription_plans'][1:])  # Skip free plan
                
                status = random.choice(['active', 'cancelled', 'expired', 'trial'])
                start_date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d %H:%M:%S')
                end_date = (datetime.now() + timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S') if status == 'active' else 'NULL'
                external_id = f'stripe_{random.randint(100000, 999999)}'
                
                stmt = f"""INSERT INTO subscriptions (id, user_id, plan_id, status, start_date, end_date, external_id)
VALUES ('{subscription_id}', '{user_id}', '{plan_id}', '{status}', '{start_date}', {f"'{end_date}'" if end_date != 'NULL' else 'NULL'}, '{external_id}');"""
                
                statements.append(stmt)
        
        return statements


def main():
    """Main function to generate SQL statements"""
    generator = TestDataGenerator()
    
    print("="*60)
    print("TEST DATA GENERATOR - EXACT SCHEMA MATCH")
    print("="*60)
    
    # Generate all SQL statements
    all_statements = []
    
    print("\nGenerating SQL statements...")
    
    # Order matters for foreign key constraints
    print("1. Generating subscription_plans...")
    all_statements.extend(generator.generate_subscription_plans())
    
    print("2. Generating users...")
    all_statements.extend(generator.generate_users())
    
    print("\n3. Generating user_profiles...")
    all_statements.extend(generator.generate_user_profiles())
    
    print("4. Generating user_contact_profiles...")
    all_statements.extend(generator.generate_user_contact_profiles())
    
    print("5. Generating campaigns...")
    all_statements.extend(generator.generate_campaigns())
    
    print("6. Generating websites...")
    all_statements.extend(generator.generate_websites())
    
    print("7. Generating submissions...")
    all_statements.extend(generator.generate_submissions())
    
    print("8. Generating submission_logs...")
    all_statements.extend(generator.generate_submission_logs())
    
    print("9. Generating captcha_logs...")
    all_statements.extend(generator.generate_captcha_logs())
    
    print("10. Generating logs...")
    all_statements.extend(generator.generate_logs())
    
    print("11. Generating system_logs...")
    all_statements.extend(generator.generate_system_logs())
    
    print("12. Generating settings...")
    all_statements.extend(generator.generate_settings())
    
    print("13. Generating subscriptions...")
    all_statements.extend(generator.generate_subscriptions())
    
    # Write to file
    filename = 'test_data_exact_schema.sql'
    with open(filename, 'w') as f:
        f.write("-- Test Data for All Tables - Exact Schema Match\n")
        f.write("-- Generated on: " + datetime.now().isoformat() + "\n")
        f.write("-- Total statements: " + str(len(all_statements)) + "\n\n")
        f.write("-- Execute in this order to respect foreign key constraints\n\n")
        
        for stmt in all_statements:
            f.write(stmt + "\n")
    
    print(f"\n✓ SQL file generated: {filename}")
    print(f"✓ Total SQL statements: {len(all_statements)}")
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"• Subscription Plans: 4")
    print(f"• Users: 10 (with roles: admin, moderator, user)")
    print(f"• User Profiles: {len(generator.generated_ids['user_profiles'])}")
    print(f"• Campaigns: {len(generator.generated_ids['campaigns'])}")
    print(f"• Websites: {len(generator.generated_ids['websites'])}")
    print(f"• Submissions: {len(generator.generated_ids['submissions'])}")
    print(f"• Various log entries created")
    
    print("\n" + "="*60)
    print("To import into PostgreSQL:")
    print("  psql -U username -d database -f test_data_exact_schema.sql")
    print("\nNote: User credentials are printed above for testing!")
    print("="*60)


if __name__ == "__main__":
    main()