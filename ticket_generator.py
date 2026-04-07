"""
Automated Ticket Generation Module
Generates e-challans for traffic violations
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
import logging

class TicketGenerator:
    """Automated traffic violation ticket generator"""
    
    def __init__(self, config):
        """Initialize ticket generator
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.location = config.get('location', 'Traffic Junction - Main Street')
        self.fine_amounts = config.get('fine_amounts', {})
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        self.tickets_dir = 'data/tickets'
        os.makedirs(self.tickets_dir, exist_ok=True)
    
    def generate_ticket(self, plate_number: str, violation_type: str, 
                       timestamp: datetime, location: str = None,
                       confidence: float = 0.0, additional_data: Dict = None) -> Dict:
        """
        Generate an e-challan for a traffic violation
        
        Args:
            plate_number: Vehicle registration number
            violation_type: Type of violation
            timestamp: Violation timestamp
            location: Violation location (optional)
            confidence: Detection confidence
            additional_data: Additional violation data
            
        Returns:
            Generated ticket dictionary
        """
        try:
            # Generate unique ticket ID
            ticket_id = self._generate_ticket_id()
            
            # Get violation details
            violation_info = self._get_violation_info(violation_type)
            
            # Prepare ticket data
            ticket = {
                'ticket_id': ticket_id,
                'plate_number': plate_number.upper().strip(),
                'violation_type': violation_type,
                'violation_description': violation_info['description'],
                'fine_amount': violation_info['fine_amount'],
                'timestamp': timestamp.isoformat(),
                'location': location or self.location,
                'confidence': round(confidence, 3),
                'status': 'pending',
                'payment_status': 'unpaid',
                'evidence': {
                    'image_path': '',
                    'video_path': '',
                    'detection_confidence': confidence
                },
                'additional_data': additional_data or {},
                'created_at': datetime.now().isoformat(),
                'due_date': self._calculate_due_date(timestamp).isoformat()
            }
            
            # Add violation-specific details
            if violation_type == 'no_helmet':
                ticket['additional_data']['riders_without_helmet'] = additional_data.get('riders_without_helmet', 0) if additional_data else 0
            elif violation_type == 'triple_riding':
                ticket['additional_data']['rider_count'] = additional_data.get('rider_count', 0) if additional_data else 0
            
            # Save ticket to file
            self._save_ticket(ticket)
            
            self.logger.info(f"Generated ticket {ticket_id} for {plate_number} - {violation_type}")
            
            return ticket
            
        except Exception as e:
            self.logger.error(f"Error generating ticket: {e}")
            return None
    
    def _generate_ticket_id(self) -> str:
        """Generate unique ticket ID"""
        # Format: TVD-YYYYMMDD-HHMMSS-UUID (shortened)
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        
        return f"TVD-{date_str}-{time_str}-{unique_id}"
    
    def _get_violation_info(self, violation_type: str) -> Dict:
        """Get violation information including fine amount"""
        violation_info = {
            'no_helmet': {
                'description': 'Riding without helmet',
                'fine_amount': self.fine_amounts.get('no_helmet', 500),
                'section': 'Motor Vehicle Act Section 129'
            },
            'triple_riding': {
                'description': 'Triple riding on two-wheeler',
                'fine_amount': self.fine_amounts.get('triple_riding', 1000),
                'section': 'Motor Vehicle Act Section 194'
            },
            'signal_jump': {
                'description': 'Signal jumping',
                'fine_amount': self.fine_amounts.get('signal_jump', 500),
                'section': 'Motor Vehicle Act Section 177'
            },
            'overspeeding': {
                'description': 'Overspeeding',
                'fine_amount': self.fine_amounts.get('overspeeding', 2000),
                'section': 'Motor Vehicle Act Section 183'
            }
        }
        
        return violation_info.get(violation_type, {
            'description': 'Traffic violation',
            'fine_amount': 500,
            'section': 'Motor Vehicle Act'
        })
    
    def _calculate_due_date(self, violation_date: datetime) -> datetime:
        """Calculate payment due date (60 days from violation)"""
        from datetime import timedelta
        return violation_date + timedelta(days=60)
    
    def _save_ticket(self, ticket: Dict):
        """Save ticket to file"""
        try:
            # Save as JSON file
            filename = f"{ticket['ticket_id']}.json"
            filepath = os.path.join(self.tickets_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(ticket, f, indent=2, default=str)
            
            self.logger.debug(f"Ticket saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving ticket: {e}")
    
    def generate_batch_tickets(self, violations: List[Dict]) -> List[Dict]:
        """
        Generate multiple tickets for batch violations
        
        Args:
            violations: List of violation dictionaries
            
        Returns:
            List of generated tickets
        """
        tickets = []
        
        for violation in violations:
            try:
                ticket = self.generate_ticket(
                    plate_number=violation.get('plate_number', ''),
                    violation_type=violation.get('violation_type', ''),
                    timestamp=datetime.fromisoformat(violation.get('timestamp', datetime.now().isoformat())),
                    location=violation.get('location'),
                    confidence=violation.get('confidence', 0.0),
                    additional_data=violation.get('additional_data', {})
                )
                
                if ticket:
                    tickets.append(ticket)
                    
            except Exception as e:
                self.logger.error(f"Error generating batch ticket: {e}")
                continue
        
        return tickets
    
    def update_ticket_status(self, ticket_id: str, status: str, 
                           payment_status: str = None) -> bool:
        """
        Update ticket status
        
        Args:
            ticket_id: Ticket ID
            status: New status (pending, paid, cancelled, etc.)
            payment_status: Payment status (paid, unpaid, partial)
            
        Returns:
            True if update successful
        """
        try:
            ticket_path = os.path.join(self.tickets_dir, f"{ticket_id}.json")
            
            if not os.path.exists(ticket_path):
                self.logger.error(f"Ticket {ticket_id} not found")
                return False
            
            # Load existing ticket
            with open(ticket_path, 'r') as f:
                ticket = json.load(f)
            
            # Update status
            ticket['status'] = status
            if payment_status:
                ticket['payment_status'] = payment_status
            ticket['updated_at'] = datetime.now().isoformat()
            
            # Save updated ticket
            with open(ticket_path, 'w') as f:
                json.dump(ticket, f, indent=2, default=str)
            
            self.logger.info(f"Updated ticket {ticket_id} status to {status}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating ticket status: {e}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Retrieve ticket by ID
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Ticket dictionary or None if not found
        """
        try:
            ticket_path = os.path.join(self.tickets_dir, f"{ticket_id}.json")
            
            if not os.path.exists(ticket_path):
                return None
            
            with open(ticket_path, 'r') as f:
                ticket = json.load(f)
            
            return ticket
            
        except Exception as e:
            self.logger.error(f"Error retrieving ticket: {e}")
            return None
    
    def get_tickets_by_plate(self, plate_number: str) -> List[Dict]:
        """
        Get all tickets for a specific plate number
        
        Args:
            plate_number: Vehicle registration number
            
        Returns:
            List of tickets
        """
        tickets = []
        
        try:
            for filename in os.listdir(self.tickets_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.tickets_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        ticket = json.load(f)
                    
                    if ticket.get('plate_number', '').upper() == plate_number.upper():
                        tickets.append(ticket)
            
            # Sort by timestamp (newest first)
            tickets.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error retrieving tickets by plate: {e}")
        
        return tickets
    
    def get_pending_tickets(self) -> List[Dict]:
        """
        Get all pending tickets
        
        Returns:
            List of pending tickets
        """
        tickets = []
        
        try:
            for filename in os.listdir(self.tickets_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.tickets_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        ticket = json.load(f)
                    
                    if ticket.get('status') == 'pending':
                        tickets.append(ticket)
            
            # Sort by timestamp (newest first)
            tickets.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error retrieving pending tickets: {e}")
        
        return tickets
    
    def generate_ticket_report(self, start_date: datetime = None, 
                             end_date: datetime = None) -> Dict:
        """
        Generate ticket report for a date range
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            
        Returns:
            Report dictionary
        """
        report = {
            'total_tickets': 0,
            'total_fine_amount': 0,
            'paid_tickets': 0,
            'unpaid_tickets': 0,
            'violations_by_type': {},
            'tickets_by_date': {}
        }
        
        try:
            for filename in os.listdir(self.tickets_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.tickets_dir, filename)
                    
                    with open(filepath, 'r') as f:
                        ticket = json.load(f)
                    
                    ticket_date = datetime.fromisoformat(ticket.get('timestamp', ''))
                    
                    # Filter by date range
                    if start_date and ticket_date < start_date:
                        continue
                    if end_date and ticket_date > end_date:
                        continue
                    
                    # Update counters
                    report['total_tickets'] += 1
                    report['total_fine_amount'] += ticket.get('fine_amount', 0)
                    
                    if ticket.get('payment_status') == 'paid':
                        report['paid_tickets'] += 1
                    else:
                        report['unpaid_tickets'] += 1
                    
                    # Count by violation type
                    violation_type = ticket.get('violation_type', 'unknown')
                    report['violations_by_type'][violation_type] = \
                        report['violations_by_type'].get(violation_type, 0) + 1
                    
                    # Count by date
                    date_str = ticket_date.strftime('%Y-%m-%d')
                    report['tickets_by_date'][date_str] = \
                        report['tickets_by_date'].get(date_str, 0) + 1
            
        except Exception as e:
            self.logger.error(f"Error generating ticket report: {e}")
        
        return report
    
    def print_ticket_summary(self, ticket: Dict):
        """Print formatted ticket summary"""
        print("\n" + "="*60)
        print("E-CHALLAN TRAFFIC VIOLATION TICKET")
        print("="*60)
        print(f"Ticket ID: {ticket.get('ticket_id', 'N/A')}")
        print(f"Vehicle Number: {ticket.get('plate_number', 'N/A')}")
        print(f"Violation: {ticket.get('violation_description', 'N/A')}")
        print(f"Fine Amount: ₹{ticket.get('fine_amount', 0)}")
        print(f"Date & Time: {ticket.get('timestamp', 'N/A')}")
        print(f"Location: {ticket.get('location', 'N/A')}")
        print(f"Status: {ticket.get('status', 'N/A')}")
        print(f"Payment Due: {ticket.get('due_date', 'N/A')}")
        
        if ticket.get('additional_data'):
            print("\nAdditional Details:")
            for key, value in ticket['additional_data'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("="*60)
        print("Please pay the fine within 60 days to avoid penalties.")
        print("="*60)
