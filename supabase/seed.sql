-- BRAHMO Governance Engine seed data
-- Mirrors the local demo repository and includes 20 knowledge nodes.

INSERT INTO organizations (id, name, config) VALUES ('supra', 'Supra Multi-Specialty Hospital', '{"cascade_max_depth": 3, "health_score_weights": {"coverage": 0.25, "freshness": 0.3, "balance": 0.2, "consistency": 0.25}}'::jsonb);

INSERT INTO hierarchy_levels (id, org_id, level_number, level_name, department) VALUES
('HL-01', 'supra', 1, 'Hospital', NULL),
('HL-03', 'supra', 3, 'Clinical Division', NULL),
('HL-05-MED', 'supra', 5, 'Gen Medicine Dept', 'medicine'),
('HL-05-ORTHO', 'supra', 5, 'Orthopaedics Dept', 'ortho'),
('HL-08-MED', 'supra', 8, 'Medicine General', 'medicine'),
('HL-08-ORTHO', 'supra', 8, 'Ortho General', 'ortho'),
('HL-10-MED', 'supra', 10, 'Medicine Ward', 'medicine'),
('HL-10-ORTHO', 'supra', 10, 'Ortho Ward', 'ortho');

INSERT INTO users (id, org_id, name, role, department) VALUES
('U-MEERA', 'supra', 'Dr. Meera (HOD Medicine)', 'HOD', 'medicine'),
('U-ANANYA', 'supra', 'Dr. Ananya (Junior)', 'EDITOR', 'medicine'),
('U-VIKRAM', 'supra', 'Dr. Vikram (HOD Ortho)', 'HOD', 'ortho'),
('U-PRIYA', 'supra', 'Nurse Priya', 'VIEWER', 'ortho'),
('U-SURESH', 'supra', 'Admin Suresh', 'ADMIN', 'admin');

INSERT INTO knowledge_nodes (id, org_id, hierarchy_level_id, type, title, content, importance, status, superseded_by, department, valid_until, created_by, created_at) VALUES
('N-M08', 'supra', 'HL-05-MED', 'DECISION', 'Sepsis Protocol v2 (2024)', 'Supra Sepsis Bundle v2 (2024): blood cultures before antibiotics, lactate within 3 HOURS, 30mL/kg crystalloid for hypotension.', 0.95, 'ACTIVE', NULL, 'medicine', '2026-01-01T00:00:00+05:30', 'U-MEERA', '2024-03-01T10:00:00+05:30'),
('N-DRV-01', 'supra', 'HL-08-MED', 'DECISION', 'Lactate Monitoring Schedule', 'Lactate levels monitored per Sepsis v2 protocol: every 3 hours for suspected sepsis patients. ICU escalation if lactate > 4 mmol/L.', 0.78, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2024-05-10T11:00:00+05:30'),
('N-DRV-02', 'supra', 'HL-08-MED', 'DECISION', 'Night Shift Sepsis Screening', 'Night shift nurses screen for sepsis using qSOFA (based on Sepsis v2 parameters): altered mentation, RR >= 22, SBP <= 100.', 0.75, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2024-06-20T08:00:00+05:30'),
('N-DRV-03', 'supra', 'HL-08-MED', 'DECISION', 'Empiric Antibiotic Selection', 'Based on Sepsis v2 bundle: Piperacillin-Tazobactam 4.5g IV within 3-hour window. Culture-guided de-escalation at 72 hours.', 0.82, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2024-07-05T15:00:00+05:30'),
('N-DRV-04', 'supra', 'HL-05-MED', 'DECISION', 'ICU Admission from Sepsis Screening', 'Patients meeting 2/3 qSOFA criteria with lactate > 2 mmol/L: assess for ICU admission within 1 hour.', 0.8, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2024-08-12T10:00:00+05:30'),
('N-DRV-05', 'supra', 'HL-05-MED', 'FACT', 'Sepsis Mortality Tracking', 'Supra sepsis mortality Q3 2024: 18% (national average 22%). Improvement attributed to v2 bundle compliance reaching 78%.', 0.6, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2024-10-01T09:00:00+05:30'),
('N-DRV-06', 'supra', 'HL-10-MED', 'DECISION', 'Pharmacy Pre-Auth for IV Antibiotics', 'Per Sepsis v2 timing: pharmacy pre-authorizes Pip-Tazo for suspected sepsis. No approval delay within 3-hour window.', 0.72, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2024-11-15T14:00:00+05:30'),
('N-DRV-04-A', 'supra', 'HL-08-MED', 'DECISION', 'ICU Bed Reservation Protocol', 'Based on ICU admission criteria (N-DRV-04): reserve 2 ICU beds per shift for suspected sepsis admissions.', 0.65, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2025-01-20T10:00:00+05:30'),
('N-DRV-04-B', 'supra', 'HL-10-MED', 'FACT', 'ICU Occupancy from Sepsis Admissions', 'ICU sepsis admissions average 3 per week (2024). Peak: 7 in monsoon season (water-borne infections).', 0.55, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2025-02-15T09:00:00+05:30'),
('N-DRV-02-A', 'supra', 'HL-10-MED', 'DECISION', 'Night Shift Escalation Timing', 'Night shift sepsis screening positive: call duty doctor within 15 minutes. If no response: escalate to HOD within 30 minutes.', 0.7, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2025-03-01T08:00:00+05:30'),
('N-HELD', 'supra', 'HL-08-MED', 'DECISION', 'Sepsis Bundle Compliance Audit Data', 'Compliance data under medico-legal review: v2 bundle adherence was 78% in Q3 2024. Two adverse outcomes under investigation.', 0.75, 'LEGAL_HOLD', NULL, 'medicine', NULL, 'U-MEERA', '2024-09-01T10:00:00+05:30'),
('N-M01', 'supra', 'HL-05-MED', 'CONSTRAINT', 'Diabetic Fasting Protocol', 'Fasting diabetic patients: adjust insulin timing not dose. Skip Glimepiride on fast days.', 0.9, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2025-06-01T09:00:00+05:30'),
('N-M03', 'supra', 'HL-05-MED', 'ANTI_PATTERN', 'Insulin Sliding Scale Alone', 'Do NOT use sliding scale as sole glycemic management. Always include basal insulin.', 0.87, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2025-07-15T14:00:00+05:30'),
('N-M02', 'supra', 'HL-08-MED', 'CONSTRAINT', 'Renal Dose Adjustment Review', 'Medicine prescriptions for eGFR < 30 require renal dose review before first maintenance dose.', 0.84, 'ACTIVE', NULL, 'medicine', NULL, 'U-MEERA', '2025-08-01T09:00:00+05:30'),
('N-M04', 'supra', 'HL-10-MED', 'ANTI_PATTERN', 'Delayed Critical Lab Escalation', 'Do not wait for routine rounds when critical lactate, potassium, or ABG values are flagged by the lab.', 0.79, 'ACTIVE', NULL, 'medicine', NULL, 'U-ANANYA', '2025-08-15T10:30:00+05:30'),
('N-O01', 'supra', 'HL-05-ORTHO', 'CONSTRAINT', 'DVT Prophylaxis Protocol', 'ALL ortho surgical patients: Enoxaparin 40mg SC daily. TKR 14d, THR 28d.', 0.93, 'ACTIVE', NULL, 'ortho', NULL, 'U-VIKRAM', '2025-04-01T10:00:00+05:30'),
('N-O02', 'supra', 'HL-08-ORTHO', 'DECISION', 'Paracetamol First-Line Post-TKR', 'Paracetamol 650mg QDS first-line. Tramadol if VAS > 6. No NSAIDs.', 0.88, 'ACTIVE', NULL, 'ortho', NULL, 'U-VIKRAM', '2025-01-20T11:00:00+05:30'),
('N-O03', 'supra', 'HL-08-ORTHO', 'DECISION', 'PT Within 24 Hours Post-TKR', 'Physiotherapy must begin within 24 hours of TKR. Day 1: ankle pumps.', 0.9, 'ACTIVE', NULL, 'ortho', NULL, 'U-VIKRAM', '2025-03-10T08:00:00+05:30'),
('N-O04', 'supra', 'HL-10-ORTHO', 'FACT', 'Ortho Ward Capacity', 'Ortho Ward: 45 beds. 85-90% occupancy. Overflow to Medicine in winter.', 0.5, 'ACTIVE', NULL, 'ortho', NULL, 'U-VIKRAM', '2025-05-01T09:00:00+05:30'),
('N-EXP', 'supra', 'HL-05-MED', 'FACT', 'Antibiotic Sensitivity Report Q2 2024', 'E. coli sensitivity to Pip-Tazo: 89%. K. pneumoniae: 72%. Based on 2024 Q2 data.', 0.55, 'EXPIRED', NULL, 'medicine', '2025-01-01T00:00:00+05:30', 'U-MEERA', '2024-07-01T09:00:00+05:30');

INSERT INTO edges (source_id, target_id, edge_type) VALUES
('N-DRV-01', 'N-M08', 'DERIVED_FROM'),
('N-DRV-02', 'N-M08', 'DERIVED_FROM'),
('N-DRV-03', 'N-M08', 'DERIVED_FROM'),
('N-DRV-04', 'N-M08', 'DERIVED_FROM'),
('N-DRV-05', 'N-M08', 'DERIVED_FROM'),
('N-DRV-06', 'N-M08', 'DERIVED_FROM'),
('N-HELD', 'N-M08', 'DERIVED_FROM'),
('N-DRV-04-A', 'N-DRV-04', 'DERIVED_FROM'),
('N-DRV-04-B', 'N-DRV-04', 'DERIVED_FROM'),
('N-DRV-02-A', 'N-DRV-02', 'DERIVED_FROM'),
('N-M01', 'N-DRV-01', 'SUPPORTS'),
('N-O01', 'N-O02', 'SUPPORTS'),
('N-O02', 'N-O01', 'DERIVED_FROM'),
('N-O03', 'N-O01', 'DERIVED_FROM');

-- Verification
-- SELECT COUNT(*) FROM knowledge_nodes; -- expected: 20
-- SELECT COUNT(*) FROM edges WHERE edge_type = 'DERIVED_FROM'; -- expected: 12