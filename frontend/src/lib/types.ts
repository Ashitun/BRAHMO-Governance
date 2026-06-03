export type Status = 'ACTIVE' | 'REVIEW_REQUIRED' | 'SUPERSEDED' | 'EXPIRED' | 'LEGAL_HOLD';
export type NodeType = 'CONSTRAINT' | 'DECISION' | 'ANTI_PATTERN' | 'FACT';
export type Severity = 'URGENT' | 'WARNING' | 'INFO';

export interface KnowledgeNode {
  id: string;
  org_id: string;
  hierarchy_level_id: string;
  type: NodeType;
  title: string;
  content: string;
  importance: number;
  status: Status;
  superseded_by: string | null;
  department: string;
  valid_until: string | null;
  created_by: string;
  created_at: string;
  hold_previous_status?: Status | null;
}

export interface Edge {
  id: string;
  source_id: string;
  target_id: string;
  edge_type: 'SUPPORTS' | 'CONTRADICTS' | 'SUPERSEDES' | 'DERIVED_FROM' | 'REQUIRES';
  created_at: string;
}

export interface User {
  id: string;
  org_id: string;
  name: string;
  role: 'ADMIN' | 'HOD' | 'EDITOR' | 'VIEWER';
  department: string;
}

export interface AuditLogEntry {
  id: string;
  node_id: string | null;
  action: string;
  old_value: string | null;
  new_value: string | null;
  actor_id: string;
  org_id: string;
  reason: string | null;
  metadata: Record<string, unknown>;
  timestamp: string;
}

export interface PulseAlert {
  id: string;
  org_id: string;
  user_id: string;
  alert_type: 'CASCADE' | 'HEALTH_DROP' | 'STALE_NODE' | 'REVIEW_COMPLETED';
  severity: Severity;
  title: string;
  body: string;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface HealthScore {
  org_id: string;
  department: string;
  coverage: number;
  freshness: number;
  balance: number;
  consistency: number;
  overall: number;
  counts: Record<string, unknown>;
  computed_at: string;
}

export interface CascadeResult {
  cascade_id: string;
  source_node_id: string;
  source_title: string;
  affected_nodes: Array<{ node_id: string; title: string; department: string; depth: number; old_status: string; new_status: string }>;
  skipped_nodes: Array<{ node_id: string; title?: string; department?: string; depth: number; reason: string }>;
  affected_count: number;
  skipped_count: number;
  max_depth_reached: number;
  max_depth_configured: number;
  visited_count: number;
}

export interface AppState {
  organizations: Array<Record<string, unknown>>;
  hierarchy_levels: Array<Record<string, unknown>>;
  knowledge_nodes: KnowledgeNode[];
  edges: Edge[];
  users: User[];
  audit_log: AuditLogEntry[];
  pulse_alerts: PulseAlert[];
  last_cascade: CascadeResult | null;
  health_pending: boolean;
  health_pending_reason: string | null;
  current_health_score: HealthScore | null;
  projected_health_score: HealthScore | null;
  demo_now: string;
}
