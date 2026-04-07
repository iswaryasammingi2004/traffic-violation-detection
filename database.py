"""
Database Management Module
Handles storage and retrieval of violation records
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

class DatabaseManager:
    """SQLite database manager for traffic violations"""
    
    def __init__(self, config):
        """Initialize database manager
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.db_path = config.get('database_path', 'data/violations.db')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create violations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT UNIQUE NOT NULL,
                    plate_number TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    violation_description TEXT,
                    fine_amount REAL,
                    timestamp DATETIME NOT NULL,
                    location TEXT,
                    confidence REAL,
                    status TEXT DEFAULT 'pending',
                    payment_status TEXT DEFAULT 'unpaid',
                    evidence TEXT,  -- JSON string for evidence data
                    additional_data TEXT,  -- JSON string for additional data
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    due_date DATETIME
                )
            ''')
            
            # Create vehicles table for vehicle tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plate_number TEXT UNIQUE NOT NULL,
                    first_seen DATETIME,
                    last_seen DATETIME,
                    violation_count INTEGER DEFAULT 0,
                    total_fines REAL DEFAULT 0.0,
                    vehicle_type TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_vehicles INTEGER DEFAULT 0,
                    total_violations INTEGER DEFAULT 0,
                    helmet_violations INTEGER DEFAULT 0,
                    triple_riding_violations INTEGER DEFAULT 0,
                    signal_jumps INTEGER DEFAULT 0,
                    overspeeding_violations INTEGER DEFAULT 0,
                    total_fine_amount REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_plate ON violations(plate_number)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_violations_status ON violations(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles(plate_number)')
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def store_violation(self, ticket: Dict) -> bool:
        """
        Store violation record in database
        
        Args:
            ticket: Ticket dictionary with violation details
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert violation record
            cursor.execute('''
                INSERT INTO violations (
                    ticket_id, plate_number, violation_type, violation_description,
                    fine_amount, timestamp, location, confidence, status,
                    payment_status, evidence, additional_data, due_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket.get('ticket_id'),
                ticket.get('plate_number'),
                ticket.get('violation_type'),
                ticket.get('violation_description'),
                ticket.get('fine_amount'),
                ticket.get('timestamp'),
                ticket.get('location'),
                ticket.get('confidence'),
                ticket.get('status', 'pending'),
                ticket.get('payment_status', 'unpaid'),
                json.dumps(ticket.get('evidence', {})),
                json.dumps(ticket.get('additional_data', {})),
                ticket.get('due_date')
            ))
            
            # Update or insert vehicle record
            self._update_vehicle_record(cursor, ticket)
            
            # Update daily statistics
            self._update_daily_statistics(cursor, ticket)
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Stored violation {ticket.get('ticket_id')} in database")
            return True
            
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Duplicate ticket ID: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error storing violation: {e}")
            return False
    
    def _update_vehicle_record(self, cursor, ticket: Dict):
        """Update vehicle record with violation information"""
        plate_number = ticket.get('plate_number')
        timestamp = ticket.get('timestamp')
        fine_amount = ticket.get('fine_amount', 0)
        
        # Check if vehicle exists
        cursor.execute('SELECT id, violation_count, total_fines FROM vehicles WHERE plate_number = ?', 
                      (plate_number,))
        result = cursor.fetchone()
        
        if result:
            # Update existing vehicle
            vehicle_id, violation_count, total_fines = result
            cursor.execute('''
                UPDATE vehicles SET 
                    last_seen = ?,
                    violation_count = violation_count + 1,
                    total_fines = total_fines + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (timestamp, fine_amount, vehicle_id))
        else:
            # Insert new vehicle
            cursor.execute('''
                INSERT INTO vehicles (
                    plate_number, first_seen, last_seen, violation_count, total_fines
                ) VALUES (?, ?, ?, 1, ?)
            ''', (plate_number, timestamp, timestamp, fine_amount))
    
    def _update_daily_statistics(self, cursor, ticket: Dict):
        """Update daily statistics"""
        timestamp = ticket.get('timestamp')
        violation_type = ticket.get('violation_type')
        fine_amount = ticket.get('fine_amount', 0)
        
        # Parse date from timestamp
        try:
            date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            date_str = date_obj.date()
        except:
            date_str = datetime.now().date()
        
        # Check if statistics exist for this date
        cursor.execute('SELECT id, total_violations, total_fine_amount FROM daily_statistics WHERE date = ?', 
                      (date_str,))
        result = cursor.fetchone()
        
        if result:
            # Update existing statistics
            stat_id, total_violations, total_fine_amount = result
            
            # Build update query based on violation type
            update_fields = ['total_violations = total_violations + 1', 
                           'total_fine_amount = total_fine_amount + ?']
            params = [fine_amount]
            
            if violation_type == 'no_helmet':
                update_fields.append('helmet_violations = helmet_violations + 1')
            elif violation_type == 'triple_riding':
                update_fields.append('triple_riding_violations = triple_riding_violations + 1')
            elif violation_type == 'signal_jump':
                update_fields.append('signal_jumps = signal_jumps + 1')
            elif violation_type == 'overspeeding':
                update_fields.append('overspeeding_violations = overspeeding_violations + 1')
            
            query = f'UPDATE daily_statistics SET {", ".join(update_fields)} WHERE id = ?'
            params.append(stat_id)
            
            cursor.execute(query, params)
        else:
            # Insert new statistics
            helmet_violations = 1 if violation_type == 'no_helmet' else 0
            triple_riding_violations = 1 if violation_type == 'triple_riding' else 0
            signal_jumps = 1 if violation_type == 'signal_jump' else 0
            overspeeding_violations = 1 if violation_type == 'overspeeding' else 0
            
            cursor.execute('''
                INSERT INTO daily_statistics (
                    date, total_violations, helmet_violations, triple_riding_violations,
                    signal_jumps, overspeeding_violations, total_fine_amount
                ) VALUES (?, 1, ?, ?, ?, ?, ?)
            ''', (date_str, helmet_violations, triple_riding_violations, 
                  signal_jumps, overspeeding_violations, fine_amount))
    
    def get_violation(self, ticket_id: str) -> Optional[Dict]:
        """Get violation by ticket ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM violations WHERE ticket_id = ?
            ''', (ticket_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._row_to_violation_dict(cursor, row)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting violation: {e}")
            return None
    
    def get_violations_by_plate(self, plate_number: str, limit: int = 100) -> List[Dict]:
        """Get violations by plate number"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM violations 
                WHERE plate_number = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (plate_number, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            violations = []
            for row in rows:
                violations.append(self._row_to_violation_dict(cursor, row))
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error getting violations by plate: {e}")
            return []
    
    def get_violations_by_date_range(self, start_date: datetime, 
                                   end_date: datetime) -> List[Dict]:
        """Get violations within date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM violations 
                WHERE timestamp BETWEEN ? AND ? 
                ORDER BY timestamp DESC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            violations = []
            for row in rows:
                violations.append(self._row_to_violation_dict(cursor, row))
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error getting violations by date range: {e}")
            return []
    
    def get_pending_violations(self) -> List[Dict]:
        """Get all pending violations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM violations 
                WHERE status = 'pending' 
                ORDER BY timestamp DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            violations = []
            for row in rows:
                violations.append(self._row_to_violation_dict(cursor, row))
            
            return violations
            
        except Exception as e:
            self.logger.error(f"Error getting pending violations: {e}")
            return []
    
    def get_vehicle_info(self, plate_number: str) -> Optional[Dict]:
        """Get vehicle information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM vehicles WHERE plate_number = ?
            ''', (plate_number,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting vehicle info: {e}")
            return None
    
    def get_statistics(self, days: int = 30) -> Dict:
        """Get violation statistics for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get overall statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_violations,
                    COUNT(DISTINCT plate_number) as unique_vehicles,
                    SUM(fine_amount) as total_fines,
                    AVG(fine_amount) as avg_fine,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_violations,
                    COUNT(CASE WHEN payment_status = 'paid' THEN 1 END) as paid_violations
                FROM violations 
                WHERE timestamp BETWEEN ? AND ?
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            stats_row = cursor.fetchone()
            
            # Get violation type breakdown
            cursor.execute('''
                SELECT violation_type, COUNT(*) as count, SUM(fine_amount) as total_fine
                FROM violations 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY violation_type
                ORDER BY count DESC
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            type_breakdown = cursor.fetchall()
            
            # Get daily statistics
            cursor.execute('''
                SELECT date, total_violations, total_fine_amount
                FROM daily_statistics 
                WHERE date >= ? 
                ORDER BY date DESC
            ''', (start_date.date(),))
            
            daily_stats = cursor.fetchall()
            conn.close()
            
            # Build statistics dictionary
            statistics = {
                'period': f'{days} days',
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_violations': stats_row[0] or 0,
                'unique_vehicles': stats_row[1] or 0,
                'total_fines': stats_row[2] or 0.0,
                'average_fine': stats_row[3] or 0.0,
                'pending_violations': stats_row[4] or 0,
                'paid_violations': stats_row[5] or 0,
                'violation_types': {},
                'daily_breakdown': []
            }
            
            # Add violation type breakdown
            for row in type_breakdown:
                statistics['violation_types'][row[0]] = {
                    'count': row[1],
                    'total_fine': row[2] or 0.0
                }
            
            # Add daily breakdown
            for row in daily_stats:
                statistics['daily_breakdown'].append({
                    'date': row[0],
                    'violations': row[1],
                    'total_fine': row[2] or 0.0
                })
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def _row_to_violation_dict(self, cursor, row) -> Dict:
        """Convert database row to violation dictionary"""
        columns = [description[0] for description in cursor.description]
        violation_dict = dict(zip(columns, row))
        
        # Parse JSON fields
        if violation_dict.get('evidence'):
            try:
                violation_dict['evidence'] = json.loads(violation_dict['evidence'])
            except:
                violation_dict['evidence'] = {}
        
        if violation_dict.get('additional_data'):
            try:
                violation_dict['additional_data'] = json.loads(violation_dict['additional_data'])
            except:
                violation_dict['additional_data'] = {}
        
        return violation_dict
    
    def update_violation_status(self, ticket_id: str, status: str, 
                              payment_status: str = None) -> bool:
        """Update violation status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if payment_status:
                cursor.execute('''
                    UPDATE violations 
                    SET status = ?, payment_status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ticket_id = ?
                ''', (status, payment_status, ticket_id))
            else:
                cursor.execute('''
                    UPDATE violations 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE ticket_id = ?
                ''', (status, ticket_id))
            
            conn.commit()
            conn.close()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            self.logger.error(f"Error updating violation status: {e}")
            return False
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Create database backup"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backups/violations_backup_{timestamp}.db"
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # Create backup
            conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            conn.backup(backup_conn)
            
            conn.close()
            backup_conn.close()
            
            self.logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up database: {e}")
            return False
