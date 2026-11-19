# Novasphere Dynamics Internal Knowledge Base & Policies

## 1. Company Overview
Novasphere Dynamics is a next-generation autonomous robotics and industrial AI enterprise founded in 2024. Headquartered in Austin, Texas, with engineering hubs in Seattle and Zurich, Novasphere manufactures autonomous logistics bots, aerial inspection drones, and adaptive edge-AI controllers.

---

## 2. Proprietary Products & Specifications

### 2.1 AetherBot v4 (Autonomous Warehouse Logistics Robot)
- **Payload Capacity:** 1,250 kg (2,755 lbs).
- **Navigation System:** NovaLidar 3D solid-state LiDAR paired with SLAM-Edge v3 vision processing.
- **Battery Life & Charging:** 14 hours continuous operation on LiFePO4 cells; 0% to 80% fast wireless inductive charging in 28 minutes.
- **Operating Temperatures:** -20°C to 55°C (-4°F to 131°F) with internal thermal heat-pump management.
- **Fail-Safe Mechanism:** Triple-redundant hardware E-stop with sub-5 millisecond magnetic braking.
- **Network Connectivity:** Private 5G NR Standalone (SA), Wi-Fi 6E, and fallback offline mesh.

### 2.2 Chronos-Edge Controller (Industrial AI Processing Unit)
- **Compute Architecture:** Dual 128-core Tensor Engine delivering 450 TOPS INT8 sparse inference.
- **Operating System:** NovaOS Enterprise 4.2 (hard real-time Linux microkernel).
- **Enclosure Rating:** IP68 sealed waterproof and dustproof alloy housing.
- **Power Draw:** 35W typical, 65W peak under multi-camera visual odometry.

---

## 3. Human Resources & Internal Workplace Policies

### 3.1 Flexible Work & "Work from Anywhere" (WFA) Policy
- All engineers and corporate staff are eligible for hybrid work (2 core office days: Tuesdays & Thursdays).
- **Annual Remote Allowance:** Employees may work 100% remotely from any approved country or state for up to 45 business days per calendar year.
- **Home Office Stipend:** One-time \$1,500 reimbursement upon hire for ergonomic desk, chair, and monitor setup, plus \$75/month internet allowance.

### 3.2 Travel & Expense Reimbursement Guidelines
- **Meals Per Diem:**
  - Standard domestic travel: Up to \$85/day (Breakfast: \$20, Lunch: \$25, Dinner: \$40). No itemized receipt required under \$25, but total daily expense must not exceed \$85.
  - High-cost domestic metros (NYC, SF, Seattle) and international: Up to \$120/day.
- **Airfare:** Coach/Economy for flights under 6 hours; Premium Economy or Business Class pre-approved by VP for flights over 6 continuous flight hours.
- **Hotel Stays:** Bookings should stay within the Concur guideline rates (up to \$250/night domestic, \$320/night high-cost tiers).

### 3.3 Learning & Professional Growth Stipend
- **Annual Education Budget:** \$3,000 per employee each fiscal year for accredited certifications (e.g., Google Cloud, Kubernetes, Robotics engineering), conferences, or university coursework.
- **Study Days:** 3 paid education leave days per year, separate from PTO.

---

## 4. Security & Incident Response Policies

### 4.1 Internal Data Classification
- **Public:** Marketing collateral, public press releases, open-source SDKs.
- **Internal Confidential:** Architectural design documents, roadmap decks, internal Slack channels.
- **Restricted / Secret:** Firmware private signing keys, production customer telemetry, payroll data.

### 4.2 IT Security Protocols
- Multi-Factor Authentication (MFA) is strictly enforced via hardware FIDO2 security keys (YubiKey). SMS-based 2FA is prohibited.
- Devices must run the crowdstrike Falcon agent and full disk encryption (BitLocker / FileVault).
- Lock screen timeout is mandated at 5 minutes inactivity.
