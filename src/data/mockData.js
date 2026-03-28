export const mockCustomers = [
  { id: 'C001', name: 'Alisha Singh', persona: 'Young Professional', financialStressScore: 12, cibilScore: 810, riskLevel: 'Low', recommendedAction: 'Offer Premium Credit Card' },
  { id: 'C002', name: 'Rajesh Kumar', persona: 'At Risk Borrower', financialStressScore: 88, cibilScore: 610, riskLevel: 'High', recommendedAction: 'Initiate Restructuring Call' },
  { id: 'C003', name: 'Sneha Patel', persona: 'Established Entrepreneur', financialStressScore: 34, cibilScore: 750, riskLevel: 'Low', recommendedAction: 'Monitor' },
  { id: 'C004', name: 'Vikram Sharma', persona: 'Serial Defaulter', financialStressScore: 95, cibilScore: 605, riskLevel: 'High', recommendedAction: 'Flag for Immediate Recovery' },
  { id: 'C005', name: 'Pooja Desai', persona: 'Overleveraged Salaried', financialStressScore: 72, cibilScore: 650, riskLevel: 'Medium', recommendedAction: 'Send Debt Consolidation Offer' },
  { id: 'C006', name: 'Amitabh Verma', persona: 'Retiree', financialStressScore: 20, cibilScore: 840, riskLevel: 'Low', recommendedAction: 'No Action Required' },
  { id: 'C007', name: 'Neha Gupta', persona: 'Recent Graduate', financialStressScore: 65, cibilScore: 680, riskLevel: 'Medium', recommendedAction: 'Financial Literacy Outreach' },
  { id: 'C008', name: 'Rahul Reddy', persona: 'Gig Economy Worker', financialStressScore: 78, cibilScore: 620, riskLevel: 'High', recommendedAction: 'Adjust Credit Limit' },
  { id: 'C009', name: 'Kavita Iyer', persona: 'Young Professional', financialStressScore: 15, cibilScore: 790, riskLevel: 'Low', recommendedAction: 'Pre-approve Home Loan' },
  { id: 'C010', name: 'Sanjay Mishra', persona: 'At Risk Borrower', financialStressScore: 85, cibilScore: 615, riskLevel: 'High', recommendedAction: 'Schedule Counselor Call' },
  { id: 'C011', name: 'Priya Kapoor', persona: 'Established Entrepreneur', financialStressScore: 40, cibilScore: 720, riskLevel: 'Low', recommendedAction: 'Monitor' },
  { id: 'C012', name: 'Kushal Jain', persona: 'Overleveraged Salaried', financialStressScore: 68, cibilScore: 660, riskLevel: 'Medium', recommendedAction: 'Proactive Payment Reminder' },
  { id: 'C013', name: 'Anjali Menon', persona: 'Young Professional', financialStressScore: 25, cibilScore: 770, riskLevel: 'Low', recommendedAction: 'Offer Auto Loan' },
  { id: 'C014', name: 'Deepak Chopra', persona: 'Gig Economy Worker', financialStressScore: 82, cibilScore: 630, riskLevel: 'High', recommendedAction: 'Temporary Limit Suspension' },
  { id: 'C015', name: 'Meera Rao', persona: 'Recent Graduate', financialStressScore: 55, cibilScore: 690, riskLevel: 'Medium', recommendedAction: 'Monitor' },
  { id: 'C016', name: 'Siddharth Bose', persona: 'Serial Defaulter', financialStressScore: 92, cibilScore: 602, riskLevel: 'High', recommendedAction: 'Legal Notice' },
  { id: 'C017', name: 'Tanya Singh', persona: 'Young Professional', financialStressScore: 18, cibilScore: 800, riskLevel: 'Low', recommendedAction: 'Offer Premium Credit Card' },
  { id: 'C018', name: 'Arjun Das', persona: 'At Risk Borrower', financialStressScore: 89, cibilScore: 608, riskLevel: 'High', recommendedAction: 'Initiate Restructuring Call' },
  { id: 'C019', name: 'Rohan Joshi', persona: 'Overleveraged Salaried', financialStressScore: 70, cibilScore: 655, riskLevel: 'Medium', recommendedAction: 'Send Debt Consolidation Offer' },
  { id: 'C020', name: 'Simran Khurana', persona: 'Established Entrepreneur', financialStressScore: 30, cibilScore: 760, riskLevel: 'Low', recommendedAction: 'Monitor' },
];

export const summaryMetrics = {
  totalCustomers: 20,
  highRiskCustomers: 7,
  avgStressScore: 58,
  avgCibilScore: 698,
  activeInterventions: 9,
};

export const riskDistributionData = [
  { name: 'Low Risk', value: 8, color: '#16a34a' },    // green-600
  { name: 'Medium Risk', value: 5, color: '#f97316' }, // orange-500
  { name: 'High Risk', value: 7, color: '#dc2626' },   // red-600
];

export const aiInsights = [
  "Increase in financial stress among salaried users (25–35)",
  "CIBIL scores declining in Tier-2 cities",
  "High unsecured debt detected in 'Gig Economy Worker' segment.",
  "System recommends proactive restructuring for 3 High-Risk accounts."
];

export const recentActivity = [
  { id: 1, action: 'Auto-froze credit line for Vikram Sharma', timestamp: '10 mins ago' },
  { id: 2, action: 'Sent restructuring offer to Rajesh Kumar', timestamp: '1 hour ago' },
  { id: 3, action: 'System flagged Siddharth Bose as High Risk', timestamp: '3 hours ago' },
  { id: 4, action: 'Generated daily portfolio stress report', timestamp: '5 hours ago' },
  { id: 5, action: 'Approved pre-approved loan for Alisha Singh', timestamp: '1 day ago' },
];
