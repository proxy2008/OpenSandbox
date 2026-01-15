// Copyright 2026 Alibaba Group Holding Ltd.
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
//     http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * Domain models for sandbox lifecycle.
 *
 * IMPORTANT:
 * - These are NOT OpenAPI-generated types.
 * - They are intentionally stable and JS-friendly.
 *
 * The internal OpenAPI schemas may change frequently; adapters map responses into these models.
 */

export type SandboxId = string;

export interface ImageAuth extends Record<string, unknown> {
  username?: string;
  password?: string;
  token?: string;
}

export interface ImageSpec {
  uri: string;
  auth?: ImageAuth;
}

export type ResourceLimits = Record<string, string>;

export type SandboxState =
  | "Creating"
  | "Running"
  | "Pausing"
  | "Paused"
  | "Resuming"
  | "Deleting"
  | "Deleted"
  | "Error"
  | string;

export interface SandboxStatus extends Record<string, unknown> {
  state: SandboxState;
  reason?: string;
  message?: string;
}

export interface SandboxInfo extends Record<string, unknown> {
  id: SandboxId;
  image: ImageSpec;
  entrypoint: string[];
  metadata?: Record<string, string>;
  status: SandboxStatus;
  /**
   * Sandbox creation time.
   */
  createdAt: Date;
  /**
   * Sandbox expiration time (server-side TTL).
   */
  expiresAt: Date;
}

export interface CreateSandboxRequest extends Record<string, unknown> {
  image: ImageSpec;
  entrypoint: string[];
  /**
   * Timeout in seconds (server semantics).
   */
  timeout: number;
  resourceLimits: ResourceLimits;
  env?: Record<string, string>;
  metadata?: Record<string, string>;
  extensions?: Record<string, unknown>;
}

export interface CreateSandboxResponse extends Record<string, unknown> {
  id: SandboxId;
  status: SandboxStatus;
  metadata?: Record<string, string>;
  /**
   * Sandbox expiration time after creation.
   */
  expiresAt: Date;
  /**
   * Sandbox creation time.
   */
  createdAt: Date;
  entrypoint: string[];
}

export interface PaginationInfo extends Record<string, unknown> {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNextPage: boolean;
}

export interface ListSandboxesResponse extends Record<string, unknown> {
  items: SandboxInfo[];
  pagination?: PaginationInfo;
}

export interface RenewSandboxExpirationRequest {
  expiresAt: string;
}

export interface RenewSandboxExpirationResponse extends Record<string, unknown> {
  /**
   * Updated expiration time (if the server returns it).
   */
  expiresAt?: Date;
}

export interface Endpoint extends Record<string, unknown> {
  endpoint: string;
}

export interface ListSandboxesParams {
  /**
   * Filter by lifecycle state (the API supports multiple `state` query params).
   * Example: `{ states: ["Running", "Paused"] }`
   */
  states?: string[];
  /**
   * Filter by metadata key-value pairs.
   * NOTE: This will be encoded to a single `metadata` query parameter as described in the spec.
   */
  metadata?: Record<string, string>;
  page?: number;
  pageSize?: number;
};