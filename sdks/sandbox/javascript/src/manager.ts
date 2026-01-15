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

import { ConnectionConfig, type ConnectionConfigOptions } from "./config/connection.js";
import { createDefaultAdapterFactory } from "./factory/defaultAdapterFactory.js";
import type { AdapterFactory } from "./factory/adapterFactory.js";

import type { ListSandboxesResponse, SandboxId, SandboxInfo } from "./models/sandboxes.js";
import type { Sandboxes } from "./services/sandboxes.js";

export interface SandboxManagerOptions {
  connectionConfig?: ConnectionConfig | ConnectionConfigOptions;
  adapterFactory?: AdapterFactory;
}

export interface SandboxFilter {
  states?: string[];
  metadata?: Record<string, string>;
  page?: number;
  pageSize?: number;
}

/**
 * Administrative interface for managing sandboxes (list/get/pause/resume/kill/renew).
 *
 * For interacting *inside* a sandbox, use {@link Sandbox}.
 */
export class SandboxManager {
  private readonly sandboxes: Sandboxes;

  private constructor(opts: { sandboxes: Sandboxes }) {
    this.sandboxes = opts.sandboxes;
  }

  static create(opts: SandboxManagerOptions = {}): SandboxManager {
    const connectionConfig = opts.connectionConfig instanceof ConnectionConfig
      ? opts.connectionConfig
      : new ConnectionConfig(opts.connectionConfig);
    const lifecycleBaseUrl = connectionConfig.getBaseUrl();
    const adapterFactory = opts.adapterFactory ?? createDefaultAdapterFactory();
    const { sandboxes } = adapterFactory.createLifecycleStack({ connectionConfig, lifecycleBaseUrl });
    return new SandboxManager({ sandboxes });
  }

  listSandboxInfos(filter: SandboxFilter = {}): Promise<ListSandboxesResponse> {
    return this.sandboxes.listSandboxes({
      states: filter.states,
      metadata: filter.metadata,
      page: filter.page,
      pageSize: filter.pageSize,
    });
  }

  getSandboxInfo(sandboxId: SandboxId): Promise<SandboxInfo> {
    return this.sandboxes.getSandbox(sandboxId);
  }

  killSandbox(sandboxId: SandboxId): Promise<void> {
    return this.sandboxes.deleteSandbox(sandboxId);
  }

  pauseSandbox(sandboxId: SandboxId): Promise<void> {
    return this.sandboxes.pauseSandbox(sandboxId);
  }

  resumeSandbox(sandboxId: SandboxId): Promise<void> {
    return this.sandboxes.resumeSandbox(sandboxId);
  }

  /**
   * Renew expiration by setting expiresAt to now + timeoutSeconds.
   */
  async renewSandbox(sandboxId: SandboxId, timeoutSeconds: number): Promise<void> {
    const expiresAt = new Date(Date.now() + timeoutSeconds * 1000).toISOString();
    await this.sandboxes.renewSandboxExpiration(sandboxId, { expiresAt });
  }

  /**
   * No-op for now (fetch-based implementation doesn't own a pooled transport).
   *
   * This method exists so callers can consistently release resources when using
   * a custom {@link AdapterFactory} implementation.
   */
  async close(): Promise<void> {
    // no-op
  }
}