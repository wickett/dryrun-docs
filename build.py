"""
DryRun Security Documentation Site Generator
Generates all HTML pages for the docs site.
Usage: python3 build.py

Site structure: 5 sections, 27 pages
"""
import csv
import html
import io
import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(value: str) -> str:
    """Escape a string for safe HTML interpolation."""
    return html.escape(str(value), quote=True)


def slugify_heading(text: str) -> str:
    """Convert a heading string to an anchor slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text


def extract_toc(html_content: str):
    """Extract h2 and h3 headings from HTML content for TOC generation."""
    pattern = re.compile(r'<(h[23])[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</\1>', re.IGNORECASE | re.DOTALL)
    items = []
    for match in pattern.finditer(html_content):
        level = match.group(1).lower()
        anchor = match.group(2)
        label = re.sub(r'<[^>]+>', '', match.group(3)).strip()
        items.append({'level': level, 'anchor': anchor, 'label': label})
    return items


def inject_heading_ids(html_content: str) -> str:
    """Inject id attributes into h2/h3 tags that lack them."""
    def replacer(m):
        tag = m.group(1)
        attrs = m.group(2)
        inner = m.group(3)
        if 'id=' in attrs.lower():
            return m.group(0)
        label = re.sub(r'<[^>]+>', '', inner).strip()
        slug = slugify_heading(label)
        return f'<{tag}{attrs} id="{slug}">{inner}</{tag}>'
    pattern = re.compile(r'<(h[23])([^>]*)>(.*?)</\1>', re.IGNORECASE | re.DOTALL)
    return pattern.sub(replacer, html_content)


# ---------------------------------------------------------------------------
# Site structure
# ---------------------------------------------------------------------------


SECTIONS = [
    {
        'name': 'Getting Started',
        'slug': 'getting-started',
        'pages': ['documentation', 'quick-start'],
    },
    {
        'name': 'Scanning',
        'slug': 'scanning',
        'pages': ['deepscan', 'pr-scanning', 'secrets-scanning', 'iac-scanning', 'sca', 'auto-fix'],
    },
    {
        'name': 'Code Security Intelligence',
        'slug': 'code-security-intelligence',
        'pages': ['feature-ships', 'architecture-risks', 'developer-trends', 'incident-response', 'shadow-ai', 'security-review-requests', 'security-reviews', 'pr-variant-analysis', 'vulnerability-trends', 'application-summary'],
    },
    {
        'name': 'Platform',
        'slug': 'platform',
        'pages': ['pr-scanning-configuration', 'custom-code-policies', 'repository-context', 'risk-register', 'finding-tuning', 'pr-blocking', 'compliance-grc', 'permissions', 'mcp', 'dryrun-api'],
    },
    {
        'name': 'Integrations',
        'slug': 'integrations',
        'pages': ['slack-integration', 'webhook-integration', 'api-access-keys', 'ai-coding-integration'],
    },
]



# ---------------------------------------------------------------------------
# Page content definitions
# ---------------------------------------------------------------------------

PAGES = {}


# -- Getting Started --

PAGES['documentation'] = {
    'title': 'Documentation',
    'description': 'Welcome to DryRun Security documentation. Learn how DryRun Security uses AI-native analysis to find vulnerabilities in your code.',
    'section': 'Getting Started',
    'content': '''
<div class="landing-hero">
<p>DryRun Security is an AI-native application security platform that reviews every pull request for vulnerabilities in real time. These docs cover setup, scanning configuration, code security intelligence, platform administration, and integrations.</p>
</div>

<div class="landing-section">
  <div class="landing-grid cols-3">
    <a class="landing-card persona" href="./risk-register.html">
      <span class="landing-card-title">AppSec Engineers</span>
      <span class="landing-card-desc">Surface top-level risk across your organization, review findings in depth, and run targeted security reviews on any repository.</span>
    </a>
    <a class="landing-card persona" href="./quick-start.html">
      <span class="landing-card-title">Developers</span>
      <span class="landing-card-desc">Connect your repositories, understand PR findings as they appear, and triage false positives without leaving your workflow.</span>
    </a>
    <a class="landing-card persona" href="./pr-scanning-configuration.html">
      <span class="landing-card-title">Admins</span>
      <span class="landing-card-desc">Configure repository scanning rules, manage notification channels, customize finding interpretation, and integrate via the API and MCP.</span>
    </a>
  </div>
</div>

<div class="landing-section">
  <div class="landing-section-header">
    <h2 id="scanning-products">Products</h2>
  </div>
  <div class="landing-grid cols-3">
    <a class="landing-card" href="./pr-scanning.html">
      <span class="landing-card-title">PR Scanning</span>
      <span class="landing-card-desc">Every PR is reviewed by DryRun Security&#x27;s AI engine, which posts contextual findings directly in your code review.</span>
    </a>
    <a class="landing-card" href="./deepscan.html">
      <span class="landing-card-title">Repository Scanning with DeepScan</span>
      <span class="landing-card-desc">Scan an entire codebase on demand to uncover vulnerabilities that predate PR-level analysis.</span>
    </a>
    <a class="landing-card" href="./secrets-scanning.html">
      <span class="landing-card-title">Secrets Scanning</span>
      <span class="landing-card-desc">Catch API keys, tokens, and hardcoded passwords in diffs before they are merged into protected branches.</span>
    </a>
    <a class="landing-card" href="./iac-scanning.html">
      <span class="landing-card-title">IaC Scanning</span>
      <span class="landing-card-desc">Evaluate Terraform, CloudFormation, and other IaC templates for misconfigurations and insecure defaults.</span>
    </a>
    <a class="landing-card" href="./sca.html">
      <span class="landing-card-title">SCA</span>
      <span class="landing-card-desc">Identify known CVEs and license issues in your open-source dependencies with every pull request.</span>
    </a>
    <a class="landing-card" href="./auto-fix.html">
      <span class="landing-card-title">Auto Fix</span>
      <span class="landing-card-desc">Accept AI-generated fixes for common vulnerability patterns and verify the remediation in a single step.</span>
    </a>
  </div>
</div>

<div class="landing-section">
  <div class="landing-section-header">
    <h2 id="code-security-intelligence">Code Security Intelligence</h2>
  </div>
  <div class="landing-grid cols-3">
    <a class="landing-card" href="./vulnerability-trends.html">
      <span class="landing-card-title">Vulnerability Trends</span>
      <span class="landing-card-desc">Monitor how vulnerability counts and severity shift over time across every connected repository.</span>
    </a>
    <a class="landing-card" href="./architecture-risks.html">
      <span class="landing-card-title">Architecture Risks</span>
      <span class="landing-card-desc">Spot recurring design-level weaknesses and systemic patterns that span multiple services or modules.</span>
    </a>
    <a class="landing-card" href="./developer-trends.html">
      <span class="landing-card-title">Developer Trends</span>
      <span class="landing-card-desc">Track how security finding rates correlate with teams, contributors, and coding activity over time.</span>
    </a>
    <a class="landing-card" href="./shadow-ai.html">
      <span class="landing-card-title">Shadow AI</span>
      <span class="landing-card-desc">Flag unapproved AI libraries, model calls, and generated code that bypass your organization&#x27;s AI governance policies.</span>
    </a>
    <a class="landing-card" href="./incident-response.html">
      <span class="landing-card-title">Incident Response Investigation</span>
      <span class="landing-card-desc">Query code intelligence to trace affected paths, identify blast radius, and accelerate root-cause analysis during incidents.</span>
    </a>
    <a class="landing-card" href="./application-summary.html">
      <span class="landing-card-title">Application Summary</span>
      <span class="landing-card-desc">Get a single-pane view of open findings, scan coverage, and overall risk across your application portfolio.</span>
    </a>
  </div>
</div>

<div class="landing-section">
  <div class="landing-section-header">
    <h2 id="platform-integrations">Platform &amp; Integrations</h2>
  </div>
  <div class="landing-grid cols-3">
    <a class="landing-card" href="./pr-blocking.html">
      <span class="landing-card-title">PR Blocking</span>
      <span class="landing-card-desc">Prevent PRs from merging when findings exceed the severity or policy thresholds you define.</span>
    </a>
    <a class="landing-card" href="./custom-code-policies.html">
      <span class="landing-card-title">Custom Code Policies</span>
      <span class="landing-card-desc">Write organization-specific security rules in plain language and enforce them on every scan.</span>
    </a>
    <a class="landing-card" href="./compliance-grc.html">
      <span class="landing-card-title">Compliance &amp; GRC</span>
      <span class="landing-card-desc">Generate compliance reports, maintain audit trails, and demonstrate regulatory readiness from a single dashboard.</span>
    </a>
    <a class="landing-card" href="./slack-integration.html">
      <span class="landing-card-title">Slack Integration</span>
      <span class="landing-card-desc">Route finding alerts and scan summaries to the Slack channels your team already monitors.</span>
    </a>
    <a class="landing-card" href="./webhook-integration.html">
      <span class="landing-card-title">Generic Webhook Integration</span>
      <span class="landing-card-desc">Stream scan events and finding data to any HTTP endpoint for custom automation and reporting pipelines.</span>
    </a>
    <a class="landing-card" href="./mcp.html">
      <span class="landing-card-title">MCP</span>
      <span class="landing-card-desc">Expose DryRun Security data to AI coding assistants and agents through the Model Context Protocol.</span>
    </a>
  </div>
</div>

''',
}

PAGES['quick-start'] = {
    'title': 'Quick Start',
    'description': 'Install DryRun Security on GitHub or GitLab and start scanning pull requests in minutes.',
    'section': 'Getting Started',
    'content': '''
<h2 id="getting-started">Getting Started</h2>

<p>DryRun Security is an AI-native application security platform that reviews every pull request for vulnerabilities in real time. This guide helps you install DryRun Security on GitHub or GitLab, run your first scan, and configure the platform to match your workflow.</p>

<h3 id="deployment-rollout-best-practices">Deployment Rollout Best Practices</h3>

<p>Follow these steps to get the most out of DryRun Security:</p>

<ol>
  <li><strong><a href="#github-installation">Install DryRun Security</a></strong> - Connect your repositories on GitHub or GitLab so every pull request is automatically reviewed.</li>
  <li><strong><a href="./deepscan.html">Do your first DeepScan</a></strong> - Run a full-repository scan to establish your baseline security posture.</li>
  <li><strong><a href="./risk-register.html">Review findings in the Risk Register</a></strong> - Examine and prioritize vulnerabilities surfaced across your repositories.</li>
  <li><strong><a href="./finding-tuning.html">Triage false positives as needed</a></strong> - Suppress findings that are not applicable so future scans stay focused on real risks.</li>
  <li><strong><a href="./repository-context.html">Configure context</a></strong> - Provide repository-level context so DryRun Security&#x27;s analysis is tailored to your codebase.</li>
  <li><strong><a href="./custom-code-policies.html">Create custom code policies</a></strong> - Define organization-specific security rules written in plain English.</li>
  <li><strong><a href="./slack-integration.html">Configure integrations and notifications</a></strong> - Route alerts to Slack, webhooks, or other channels your team already uses.</li>
  <li><strong><a href="./feature-ships.html">Unlock the power of Code Security Intelligence</a></strong> - Query the intelligence index to track features, trends, and risks across your organization.</li>
</ol>

<h3 id="supported-platforms">Supported Platforms</h3>

<table>
  <thead>
    <tr>
      <th>Platform</th>
      <th>Supported Versions</th>
      <th>Setup Guide</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>GitHub</td>
      <td>GitHub.com (Cloud)</td>
      <td><a href="#github-installation">GitHub Installation</a></td>
    </tr>
    <tr>
      <td>GitLab</td>
      <td>GitLab.com (Cloud)</td>
      <td><a href="#gitlab-installation">GitLab Installation</a></td>
    </tr>
  </tbody>
</table>

<h2 id="github-installation">GitHub Installation</h2>

<h3 id="authorize-and-install">Authorize and Install the DryRun Security GitHub Application</h3>

<ol>
  <li>
    <p>Navigate to <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a> and click the <strong>Log in with GitHub</strong> button.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/01-login.png" alt="DryRun Security Login page" loading="lazy"></figure>
  </li>
  <li>
    <p>Log in to the GitHub account where DryRun Security will be installed.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/02-github-login.png" alt="GitHub Login for DryRun Security" loading="lazy"></figure>
  </li>
  <li>
    <p>Authorize the DryRun Security GitHub Application by clicking the <strong>Authorize DryRunSecurity</strong> button.</p>
    <p><strong>Note:</strong> This is a standard authorization screen for all applications in GitHub.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/06-github-authorize.png" alt="Authorize DryRun Security on GitHub" loading="lazy"></figure>
  </li>
  <li>
    <p>You'll be redirected to the DryRun Security portal. Click the <strong>Install</strong> button.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/04-install.png" alt="DryRun Security Install button" loading="lazy"></figure>
  </li>
  <li>
    <p>Click the <strong>Install</strong> button on the DryRunSecurity GitHub Application page.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/03-github-install.png" alt="DryRun Security GitHub Application install" loading="lazy"></figure>
  </li>
  <li>
    <p>Choose the GitHub repositories DryRun Security will run by selecting <strong>All Repositories</strong> or <strong>Only selected repositories</strong>.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/05-github-installation.png" alt="Select repositories for DryRun Security" loading="lazy"></figure>
  </li>
  <li>
    <p>After step one your installation may be paused for up to 2 business days as we activate your account.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/07-awaiting-activation.png" alt="DryRun Security awaiting account activation" loading="lazy"></figure>
  </li>
  <li>
    <p>Once your account has been activated, you'll see the <strong>Installation Complete</strong> message the next time you visit <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</p>
    <figure class="docs-screenshot"><img src="{asset_prefix}assets/images/install/08-installation-complete.png" alt="DryRun Security installation complete" loading="lazy"></figure>
  </li>
</ol>

<p><strong>Congratulations!</strong> Installation is complete. At this point DryRun Security will run checks on your repository as code is committed to Pull Requests.</p>

<h2 id="gitlab-installation">GitLab Installation</h2>

<p>DryRun Security for GitLab.com enables fast, contextual code reviews that help your team spot unknown risks before they start.</p>

<p>This guide will walk you through connecting your GitLab environment to DryRun Security by:</p>

<ul>
  <li>Creating a GitLab Group Access Token with the correct scopes.</li>
  <li>Installing DryRun Security via the DryRun Security Dashboard.</li>
</ul>

<p>Once installed and activated, you&#x27;ll get immediate visibility into security risks across your GitLab projects &mdash; without slowing development down.</p>

<h3 id="create-a-group-access-token">Create a Group Access Token</h3>

<p>This section describes creating a Group Access Token that will be used during the installation of DryRun Security.</p>

<h4 id="generating-the-group-access-token">Generating the Group Access Token</h4>

<ol>
  <li>Log in to <a href="https://gitlab.com" target="_blank" rel="noopener noreferrer">gitlab.com</a>.</li>
  <li>Navigate to the Group where DryRun Security will be installed.</li>
  <li>Go to <strong>Settings &gt; Access Tokens</strong>.</li>
  <li>Click <strong>Add new token</strong>.</li>
  <li>Add a token name, set the role to at least <strong>Maintainer</strong>, and select the <code>api</code> and <code>read_user</code> scopes.</li>
  <li>Click <strong>Create group access token</strong>.</li>
  <li>Copy the token and save it for later use.</li>
</ol>

<p>Done! The Group Access Token can be used to install DryRun Security.</p>

<h3 id="install-via-dashboard">Install DryRun Security via the Dashboard</h3>

<ol>
  <li>Navigate to <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a> and click the <strong>Log in with GitLab</strong> button.</li>
  <li>Authorize the DryRun Security OAuth Application.</li>
</ol>

<p><strong>Important:</strong> Choose the User or Group where DryRun Security will run from the User/Group Selector. This is usually a Group.</p>

<ol start="3">
  <li>Click the <strong>Add Token</strong> button or navigate to <strong>Settings &gt; GitLab</strong>.</li>
  <li>Enter the Group Access Token created earlier and click <strong>Save Token</strong>.</li>
  <li>Verify the User/Group for the Installation and click <strong>Confirm</strong> to confirm API access.</li>
  <li>Install on Projects by clicking <strong>+</strong> next to the Project and then click <strong>Save Projects</strong>.</li>
</ol>

<h4 id="activation">Activation</h4>

<p>Your installation may be paused for up to 2 business days as we activate your account. We&#x27;ll notify you as soon as your account has been activated.</p>

<p>Once your account has been activated, you&#x27;ll see the <strong>Installation Complete</strong> message the next time you log in to the portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</p>

<p><strong>Congratulations!</strong> Installation is complete.</p>

<p><strong>Note:</strong> At this point the DryRun Security application will run and analyze changes as code is committed to the Project(s).</p>


<h2 id="references">References</h2>

<ul>
  <li><a href="./pr-scanning.html">PR Code Reviews</a> - understand how DryRun Security analyzes your pull requests.</li>
  <li><a href="./pr-scanning-configuration.html">Configurations</a> - customize which agents and policies run on each repository.</li>
  <li><a href="./custom-code-policies.html">Custom Code Policies</a> - create custom security rules in plain English.</li>
</ul>
''',
}


# -- Scanning --

PAGES['deepscan'] = {
    'title': 'Repository Scanning with DeepScan',
    'description': 'DeepScan analyzes your entire codebase, not just recent pull requests, to find vulnerabilities that accumulate over time.',
    'section': 'Scanning',
    'content': '''
<h2 id="what-is-deepscan">What Is DeepScan?</h2>

<p>DryRun Security's standard PR Code Review analyzes changes as they arrive in each pull request. This is highly effective for catching new vulnerabilities before they merge, but it doesn't address risk that was already present in the codebase before DryRun Security was installed - or vulnerabilities that were introduced gradually across many small commits.</p>

<p><strong>DeepScan</strong> solves this by triggering a full-repository analysis. Rather than examining a diff, DeepScan ingests and analyzes the complete codebase, tracing data flows across files, identifying vulnerable patterns in legacy code, and surfacing risks that would never appear in a PR-only workflow.</p>

<h2 id="when-to-use-deepscan">When to Use DeepScan</h2>

<p>DeepScan is most valuable in several scenarios:</p>

<ul>
  <li><strong>Initial onboarding</strong> - Run a DeepScan when first connecting a repository to DryRun Security to establish your baseline security posture.</li>
  <li><strong>After a security incident</strong> - Use DeepScan to sweep a repository for related vulnerabilities after a finding is reported.</li>
  <li><strong>Compliance and audit preparation</strong> - Generate a comprehensive findings report for auditors or regulators who need evidence of security review.</li>
  <li><strong>Periodic security reviews</strong> - Schedule DeepScans on a regular cadence to catch drift and regression that PR-level analysis might miss across long periods.</li>
  <li><strong>Major refactors or dependency upgrades</strong> - When significant portions of the codebase change outside of a single PR, DeepScan ensures the full scope of changes is reviewed.</li>
</ul>

<h2 id="triggering-a-deepscan">Triggering a DeepScan</h2>

<ol>
  <li>Log in to the <strong>DryRun Security Dashboard</strong>.</li>
  <li>Navigate to the <strong>DeepScan</strong> page.</li>
  <li>Click <strong>&ldquo;New Scan&rdquo;</strong>.</li>
  <li>Select the repository and branch if desired.</li>
  <li>Monitor scan progress on the <strong>DeepScan</strong> page.</li>
</ol>

<h2 id="deepscan-workflow">DeepScan Workflow</h2>

<ol>
  <li><strong>Understand the codebase</strong> - Profile the app&rsquo;s language, frameworks, components, and data stores.</li>
  <li><strong>Gather security-relevant info</strong> - Map routes, auth files, configs, and authorization patterns.</li>
  <li><strong>Plan the review</strong> - Generate a targeted attack plan for each security domain.</li>
  <li><strong>Run the reviews</strong> - Analyze each domain (auth, injection, crypto, config, SCA, etc.) and log findings.</li>
  <li><strong>Clean up the report</strong> - Calibrate severities, remove hallucinations, deduplicate, and add exec summary and recommendations.</li>
  <li><strong>Publish and triage</strong> - Findings land in the dashboard where users can categorize and annotate each one.</li>
</ol>

<h2 id="deepscan-findings">DeepScan Findings</h2>

<p>There are two ways to review findings from a completed DeepScan:</p>

<h3 id="option-1-risk-register">Option 1 - Risk Register</h3>

<p>Filter the <a href="../docs/risk-register.html">Risk Register</a> by DeepScan to see all findings surfaced by DeepScan across repositories. This gives a unified view alongside PR scan findings for triage and prioritization.</p>

<h3 id="option-2-deepscan-page">Option 2 - DeepScan Page</h3>

<p>From the DeepScan page, click on a previously scanned repository to see findings from the latest DeepScan. To review past scans, use the date picker at the top of the page and select the date of a previous scan. The &ldquo;View Details&rdquo; button shows app-specific summaries created by DeepScan &mdash; including auth methods, APIs, configurations, and other context discovered during the scan.</p>

<h2 id="vulnerability-categories">Vulnerability Categories</h2>

<p>DryRun Security can detect the following vulnerability categories. CWE mappings are provided as reference anchors for each category.</p>

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Description</th>
      <th>Example CWEs</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>API Query Injection</td><td>Improper handling of user-controlled input in API queries that allows attackers to manipulate backend queries or filters.</td><td>CWE-943, CWE-74</td></tr>
    <tr><td>Authentication Bypass</td><td>Flaws that allow users to bypass authentication mechanisms and gain access without valid credentials.</td><td>CWE-287, CWE-306</td></tr>
    <tr><td>Missing Authorization Checks</td><td>Endpoints or functions that fail to enforce authorization, allowing users to access resources they should not.</td><td>CWE-862</td></tr>
    <tr><td>Business Logic Flaw</td><td>Errors in application logic that can be abused to gain unintended outcomes, even when traditional security controls are in place.</td><td>CWE-840</td></tr>
    <tr><td>Cache Poisoning</td><td>Manipulation of cache entries to serve malicious or incorrect content to other users.</td><td>CWE-444, CWE-113</td></tr>
    <tr><td>Configuration Injection</td><td>Injection of untrusted input into configuration files, environment variables, or runtime settings.</td><td>CWE-15, CWE-20</td></tr>
    <tr><td>Cryptographic Weakness</td><td>Use of weak, broken, or outdated cryptographic algorithms, keys, or practices.</td><td>CWE-327, CWE-326</td></tr>
    <tr><td>Cross-Site Request Forgery (CSRF)</td><td>Actions performed on behalf of an authenticated user without their consent due to missing or weak CSRF protections.</td><td>CWE-352</td></tr>
    <tr><td>CSV Injection</td><td>Injection of spreadsheet formulas into CSV exports that execute when opened in spreadsheet software.</td><td>CWE-1236</td></tr>
    <tr><td>Email Header Injection</td><td>Manipulation of email headers through unsanitized input, potentially enabling spam or phishing attacks.</td><td>CWE-93</td></tr>
    <tr><td>Excessive Privileges</td><td>Users, services, or tokens granted more permissions than required for their intended function.</td><td>CWE-250, CWE-269</td></tr>
    <tr><td>Hardcoded Credentials</td><td>Credentials such as passwords, API keys, or tokens embedded directly in source code.</td><td>CWE-798, CWE-259</td></tr>
    <tr><td>HTTP Header Injection</td><td>Injection of malicious content into HTTP headers due to improper input validation.</td><td>CWE-113, CWE-93</td></tr>
    <tr><td>Insecure Direct Object Reference (IDOR)</td><td>Direct access to internal objects using user-controlled identifiers without proper authorization checks.</td><td>CWE-639, CWE-284</td></tr>
    <tr><td>Information Disclosure</td><td>Exposure of sensitive data such as secrets, internal paths, stack traces, or system details.</td><td>CWE-200, CWE-209</td></tr>
    <tr><td>Insecure Client Storage</td><td>Sensitive data stored insecurely on the client side, such as in local storage or cookies.</td><td>CWE-922, CWE-312</td></tr>
    <tr><td>Insecure Defaults</td><td>Unsafe default configurations that weaken security if not explicitly changed.</td><td>CWE-276, CWE-1188</td></tr>
    <tr><td>Insecure Deserialization</td><td>Deserializing untrusted data in a way that allows code execution or data manipulation.</td><td>CWE-502</td></tr>
    <tr><td>Insecure File Upload</td><td>File upload functionality that allows malicious files or unrestricted file types.</td><td>CWE-434</td></tr>
    <tr><td>Insecure Transport</td><td>Use of unencrypted or improperly secured network communication channels.</td><td>CWE-319, CWE-295</td></tr>
    <tr><td>Intent Redirection</td><td>Unvalidated or unsafe redirection logic that can be abused to send users to unintended destinations specifically in mobile applications.</td><td>CWE-601</td></tr>
    <tr><td>Language Version Risk</td><td>Use of outdated or unsupported programming language versions with known security issues.</td><td>CWE-1104</td></tr>
    <tr><td>LLM Tool Misuse</td><td>Unsafe or unintended use of large language model tools, including insecure prompt handling or tool invocation.</td><td>CWE-20, CWE-74, CWE-1426</td></tr>
    <tr><td>Log Injection</td><td>Injection of untrusted input into logs that can mislead monitoring systems or hide malicious activity.</td><td>CWE-117</td></tr>
    <tr><td>Mass Assignment</td><td>Automatic binding of user input to object properties without restricting sensitive fields.</td><td>CWE-915</td></tr>
    <tr><td>Memory Safety Issue</td><td>Unsafe memory operations that can lead to crashes, data corruption, or code execution.</td><td>CWE-119, CWE-787, CWE-416</td></tr>
    <tr><td>Network Exposure</td><td>Unintended exposure of internal services, ports, or network resources.</td><td>CWE-668</td></tr>
    <tr><td>Open CORS Policy</td><td>Overly permissive Cross-Origin Resource Sharing policies that allow unintended access.</td><td>CWE-942</td></tr>
    <tr><td>Open Redirect</td><td>Redirects that accept untrusted input, enabling phishing or malicious redirection attacks.</td><td>CWE-601</td></tr>
    <tr><td>Path Traversal</td><td>Manipulation of file paths to access files or directories outside the intended scope.</td><td>CWE-22</td></tr>
    <tr><td>Privilege Escalation</td><td>Flaws that allow users or processes to gain higher privileges than intended.</td><td>CWE-269, CWE-284</td></tr>
    <tr><td>Prompt Injection</td><td>Manipulation of LLM prompts that alters behavior, bypasses safeguards, or leaks sensitive data.</td><td>CWE-77, CWE-74, CWE-913, CWE-1427</td></tr>
    <tr><td>Prototype Pollution</td><td>Modification of object prototypes that can impact application logic or security.</td><td>CWE-1321</td></tr>
    <tr><td>Remote Code Execution (RCE)</td><td>Flaws that allow attackers to execute arbitrary code on the host system.</td><td>CWE-94, CWE-78</td></tr>
    <tr><td>Resource Exhaustion</td><td>Operations that can be abused to consume excessive CPU, memory, or other resources.</td><td>CWE-400</td></tr>
    <tr><td>SQL Injection (SQLi)</td><td>Injection of malicious SQL queries through unsanitized input.</td><td>CWE-89</td></tr>
    <tr><td>Server-Side Request Forgery (SSRF)</td><td>Ability to make server-side requests to internal or unintended external resources.</td><td>CWE-918</td></tr>
    <tr><td>Subdomain Takeover</td><td>Dangling or misconfigured subdomains that can be claimed by attackers, as defined by Infrastructure as Code (IaC).</td><td>CWE-668, CWE-284</td></tr>
    <tr><td>Supply Chain Risk</td><td>Risks introduced through third-party libraries, dependencies, or external services.</td><td>CWE-1104, CWE-829</td></tr>
    <tr><td>Terminal Escape Injection</td><td>Injection of terminal control characters that can manipulate terminal output or behavior.</td><td>CWE-150, CWE-74</td></tr>
    <tr><td>Time-of-Check Time-of-Use (TOCTOU)</td><td>Race conditions where system state changes between validation and use.</td><td>CWE-367</td></tr>
    <tr><td>Timing Side Channel</td><td>Information leakage through measurable differences in execution time.</td><td>CWE-208</td></tr>
    <tr><td>UI Spoofing</td><td>User interface elements designed to deceive users into taking unintended actions.</td><td>CWE-451</td></tr>
    <tr><td>User Enumeration</td><td>Ability to determine valid users based on application responses.</td><td>CWE-203, CWE-204</td></tr>
    <tr><td>Vulnerable Dependency</td><td>Use of third-party dependencies with known security vulnerabilities.</td><td>CWE-937, CWE-1104</td></tr>
    <tr><td>XML Injection</td><td>Injection of malicious XML content that alters processing or behavior.</td><td>CWE-91</td></tr>
    <tr><td>Cross-Site Scripting (XSS)</td><td>Injection of malicious scripts that execute in a user&rsquo;s browser.</td><td>CWE-79</td></tr>
    <tr><td>XML External Entity (XXE)</td><td>XML parsing vulnerabilities that allow access to internal files or services.</td><td>CWE-611</td></tr>
  </tbody>
</table>

<h2 id="supported-languages">Supported Languages</h2>

<p>DeepScan supports repositories written in a wide range of programming languages and frameworks, including:</p>

<ul>
  <li>JavaScript / TypeScript (Node.js, React, Angular, Vue)</li>
  <li>Python (Django, Flask, FastAPI)</li>
  <li>Java (Spring, Jakarta EE)</li>
  <li>Go</li>
  <li>Ruby (Rails, Sinatra)</li>
  <li>PHP (Laravel, Symfony)</li>
  <li>C# (.NET)</li>
  <li>Kotlin</li>
  <li>Swift</li>
  <li>Rust</li>
</ul>

<p>DeepScan automatically detects the language and framework in use during the initial codebase profiling step and tailors its analysis accordingly.</p>

<h2 id="behavioral-analysis">Git Behavioral Analysis</h2>

<p class="lead">DryRun Security constructs a <strong>Git Behavioral Graph</strong> before its AI agent reads a single line of code - analyzing commit history across five behavioral axes to steer the scanner toward the code that matters most.</p>

<div class="callout callout-info">
<p>The techniques described here are grounded in Adam Tornhill's <em>Your Code as a Crime Scene</em> (2nd ed., Pragmatic Programmers, 2024). DryRun Security engineered these forensic principles into a pipeline that steers an AI agent with deterministic precision. <a href="https://www.dryrun.security/blog/steering-agentic-security-scanners-with-git-behavioral-graphs" target="_blank" rel="noopener noreferrer">Read the full blog post</a> for additional context.</p>
</div>

<h3 id="why-git-history-matters">Why Git History Matters for Security</h3>

<p>Traditional static analysis lacks a fundamental dimension of context: the human element. Vulnerabilities are rarely just syntactical errors - they are the byproduct of diffuse ownership, shifting requirements, and knowledge decay. The Git Behavioral Graph provides a deterministic, high-signal heuristic to prioritize the agent's attention before it reads any code.</p>

<h3 id="five-behavioral-axes">The Five Behavioral Axes</h3>

<ul>
  <li><strong>Code churn</strong> - Files with high revision counts and many distinct contributors historically correlate with vulnerability density. The pipeline quantifies this as a normalized churn score.</li>
  <li><strong>Contributor coupling</strong> - When many authors touch the same file, implicit knowledge can be lost. The ratio of unique contributors to total revisions produces a diffuse-ownership signal.</li>
  <li><strong>Temporal coupling</strong> - Files that change together frequently suggest hidden dependencies. If a change to <code>auth_middleware.py</code> always accompanies changes to <code>session_handler.py</code>, a change to one without the other is suspicious.</li>
  <li><strong>Recency weighting</strong> - Recent changes carry more risk than ancient stable code. The pipeline applies exponential decay weighting so churn from last week outweighs churn from last year.</li>
  <li><strong>Complexity hotspot scoring</strong> - Combining churn and contributor metrics with code complexity produces composite hotspot scores that identify the files most likely to harbor latent vulnerabilities.</li>
</ul>
''',
}

PAGES['pr-scanning'] = {
    'title': 'PR Scanning',
    'description': 'Understand how DryRun Security automatically analyzes your pull requests for security vulnerabilities.',
    'section': 'Scanning',
    'content': '''
<h2 id="how-it-works">How It Works</h2>

<p>DryRun Security analyzes code changes every time a pull request is opened or updated. Its security agents inspect the diff, evaluate the surrounding context, and report findings directly on the PR - before the code is merged. Scanning runs automatically with no manual steps required: open a PR and DryRun Security handles the rest.</p>

<p>Results appear as a summary comment on the pull request, inline comments on specific lines, and a pass/fail check status that integrates with your branch protection rules. This keeps security feedback inside the developer workflow where it can be acted on immediately.</p>

<h2 id="supported-platforms">Supported Platforms</h2>

<p>DryRun Security integrates natively with the two most widely used source code platforms:</p>

<table>
  <thead>
    <tr>
      <th>Platform</th>
      <th>Trigger</th>
      <th>Check Status</th>
      <th>Inline Comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>GitHub</td>
      <td>Pull request opened or synchronized</td>
      <td>GitHub Checks API</td>
      <td>PR review comments on affected lines</td>
    </tr>
    <tr>
      <td>GitLab</td>
      <td>Merge request opened or updated</td>
      <td>GitLab pipeline status</td>
      <td>Merge request discussion comments</td>
    </tr>
  </tbody>
</table>

<h2 id="what-gets-analyzed">What Gets Analyzed</h2>

<p>When a pull request is opened, DryRun Security retrieves the diff along with relevant surrounding code context - imported modules, authentication middleware, framework conventions, and any configured security policies. Analysis is scoped to the changed regions and the code paths that flow through them.</p>

<p>DryRun Security also reads the repository's <code>agents.md</code> file, if present. This allows teams to provide context and instructions that guide the security analysis - such as project-specific conventions, known safe patterns, or areas of particular concern.</p>

<p>The following security agents run on every PR scan:</p>

<ul>
  <li><strong>Cross-Site Scripting Analyzer</strong></li>
  <li><strong>General Security Analyzer</strong></li>
  <li><strong>IDOR Analyzer</strong></li>
  <li><strong>Mass Assignment</strong></li>
  <li><strong>Secrets Analyzer</strong></li>
  <li><strong>Server-Side Request Forgery Analyzer</strong></li>
  <li><strong>SQL Injection Analyzer</strong></li>
  <li>Any <a href="./custom-code-policies.html">custom code policies</a> created by your team</li>
</ul>

<p>All findings are filtered to the changed regions of the pull request. Pre-existing issues in unchanged code are excluded from the results so developers can focus on what they introduced.</p>

<h2 id="check-status-and-feedback">Check Status &amp; Feedback</h2>

<p>DryRun Security reports results through two channels: a <strong>summary comment</strong> on the pull request with an overview of all findings, and individual <strong>check statuses</strong> that integrate with your branch protection rules.</p>

<p>Each check corresponds to a specific security agent or policy. The check status reflects the outcome of that agent's analysis:</p>

<table>
  <thead>
    <tr>
      <th>Status</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Success</strong></td>
      <td>No findings at or above the configured severity threshold. The PR is clear to merge.</td>
    </tr>
    <tr>
      <td><strong>Failure</strong></td>
      <td>One or more findings meet or exceed the blocking threshold. The PR cannot be merged until issues are resolved.</td>
    </tr>
  </tbody>
</table>

<p>When findings are detected, inline comments are posted directly on the affected lines of code with a description of the vulnerability and remediation guidance. For details on enforcing merge gates with check statuses, see <a href="./pr-blocking.html">PR Blocking</a>.</p>

<p>If you are seeing noisy or irrelevant findings, you can <a href="./finding-tuning.html">tune your findings</a> to reduce noise and focus on the issues that matter most to your team.</p>

<h2 id="configuration">Configuration</h2>

<p>PR scanning behavior is controlled through configurations in the DryRun Security dashboard. Each configuration can be applied to one or more repositories, and a <code>default</code> configuration covers any repository not assigned to a specific one.</p>

<table>
  <thead>
    <tr>
      <th>Setting</th>
      <th>Default</th>
      <th>What It Controls</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Security Agents</td>
      <td>All enabled</td>
      <td>Which code security analyzers (XSS, SQLi, IDOR, Secrets, etc.) run on PRs</td>
    </tr>
    <tr>
      <td>Custom Code Policies</td>
      <td>None attached</td>
      <td>Organization-specific rules written in plain English, enforced on every PR</td>
    </tr>
    <tr>
      <td>PR Blocking</td>
      <td>Disabled</td>
      <td>Whether findings at a given severity fail the check status and prevent merge</td>
    </tr>
    <tr>
      <td>Blocking Threshold</td>
      <td>High</td>
      <td>Minimum severity level (Critical, High, Medium, Low) that triggers a failed check</td>
    </tr>
    <tr>
      <td>PR Issue Comments</td>
      <td>Enabled</td>
      <td>Whether DryRun Security posts a summary comment and inline findings on the PR</td>
    </tr>
    <tr>
      <td>Notifications</td>
      <td>Disabled</td>
      <td>Alerts sent via Slack or webhook when findings are detected</td>
    </tr>
  </tbody>
</table>

<p>Configurations follow an inheritance model: the <code>default</code> configuration applies to all repositories, and repository-specific configurations override it. This lets you set organization-wide baselines while customizing behavior for individual repositories or teams.</p>

<p>See <a href="./pr-scanning-configuration.html">PR Scanning Configuration</a> for a full walkthrough of creating and managing configurations.</p>

<h2 id="pr-scanning-vs-deepscan">How PR Scanning Differs From DeepScan</h2>

<p>DryRun Security offers two scanning modes. PR Scanning analyzes changes as they arrive in pull requests. <a href="./deepscan.html">DeepScan</a> performs a full-repository analysis to find vulnerabilities in existing code. The two modes are complementary:</p>

<table>
  <thead>
    <tr>
      <th>Aspect</th>
      <th>PR Scan</th>
      <th>DeepScan</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Scope</td>
      <td>Changed files and surrounding context in the PR</td>
      <td>Entire repository codebase</td>
    </tr>
    <tr>
      <td>Trigger</td>
      <td>Automatic on PR open or update</td>
      <td>Manual or scheduled from the dashboard</td>
    </tr>
    <tr>
      <td>Speed</td>
      <td>Seconds to minutes, depending on diff size</td>
      <td>Minutes to hours, depending on repo size</td>
    </tr>
    <tr>
      <td>Differential Analysis</td>
      <td>Yes - only new findings from the PR are reported</td>
      <td>No - all findings in the codebase are reported</td>
    </tr>
    <tr>
      <td>Results Location</td>
      <td>PR comments, inline annotations, check statuses, and the DryRun Security dashboard</td>
      <td>DryRun Security dashboard and Risk Register</td>
    </tr>
    <tr>
      <td>Best For</td>
      <td>Catching new vulnerabilities before merge</td>
      <td>Baseline assessment, audits, and legacy code review</td>
    </tr>
  </tbody>
</table>

''',
}

PAGES['secrets-scanning'] = {
    'title': 'Secrets Scanning',
    'description': 'How DryRun Security detects hardcoded credentials, API keys, tokens, and other secrets in your codebase.',
    'section': 'Scanning',
    'content': '''
<h2 id="the-secrets-analyzer">The Secrets Analyzer</h2>

<p>Hardcoded credentials are among the most common and most exploitable security vulnerabilities in modern software. API keys, database passwords, authentication tokens, and private keys committed to source code are routinely discovered by attackers scanning public repositories - and by insiders with unintended access to private ones.</p>

<p>DryRun Security's <strong>Secrets Analyzer</strong> is a specialized agent that runs on every pull request, examining code changes for signs of embedded credentials. It operates contextually - not just matching patterns that look like secrets, but evaluating whether a candidate secret is genuine based on its surrounding context, variable naming, usage patterns, and code structure.</p>

<h2 id="what-secrets-detection-covers">What Secrets Detection Covers</h2>

<p>The Secrets Analyzer detects a wide range of credential types, including:</p>

<ul>
  <li>API keys and access tokens for cloud providers (AWS, GCP, Azure) and third-party services</li>
  <li>Database connection strings with embedded credentials</li>
  <li>Private keys (RSA, EC, SSH)</li>
  <li>Authentication tokens and session secrets</li>
  <li>OAuth client secrets</li>
  <li>Webhook secrets and signing keys</li>
  <li>Generic high-entropy strings that exhibit the statistical properties of cryptographic secrets</li>
</ul>

<h2 id="deepscan-secrets">DeepScan Secrets Workflow</h2>

<p>Secrets detected during DeepScan are now reviewed through a dedicated, more robust workflow that provides clearer visibility into sensitive exposures. Rather than processing secrets findings through the general analysis pipeline, DeepScan routes them through a specialized handler that improves classification accuracy and surfaces them with richer context in the <a href="../docs/risk-register.html">Risk Register</a>.</p>

<h2 id="contextual-accuracy">Contextual Accuracy</h2>

<p>What distinguishes DryRun's secrets detection from simple regex scanning is context awareness. A string that matches the format of an AWS access key is not automatically a finding - the Secrets Analyzer considers whether it appears in a test fixture, an example configuration file, a comment marked as a placeholder, or a real configuration path being read at runtime. This dramatically reduces false positives without sacrificing genuine detection.</p>

<p>When a confirmed secret is found, the finding includes the file path, line number, and a plain-language explanation of the risk - without reproducing the credential value in the finding report itself.</p>

<h2 id="blocking-and-branch-protection">Blocking and Branch Protection</h2>

<p>The Secrets Analyzer can be configured to block PR merges via GitHub Branch Protection Rules. When a secret is detected and the Secrets Analyzer has blocking enabled, the check will fail and the PR cannot be merged until the credential is removed and the branch is re-scanned. See <a href="../pr-scanning-configuration.html">Configurations</a> for setup instructions.</p>

<h2 id="suppression-and-false-positives">Suppression and False Positives</h2>

<p>Not every high-entropy string is a real credential. The Risk Register's <a href="../finding-tuning.html">Finding Triage</a> workflow allows teams to mark findings as false positives with contextual notes - for example, to record that a particular string is a well-known public test key. Triaged fingerprints are suppressed in future scans automatically, and DryRun Security learns from the context to improve detection accuracy over time.</p>
''',
}

PAGES['iac-scanning'] = {
    'title': 'IaC Scanning',
    'description': 'DryRun Security scans IaC configurations for security misconfigurations, subdomain takeover risks, and infrastructure vulnerabilities.',
    'section': 'Scanning',
    'content': '''
<h2 id="what-is-iac-scanning">What Is IaC Scanning?</h2>

<p>Infrastructure as Code (IaC) has transformed how teams provision and manage cloud resources. Terraform, CloudFormation, Pulumi, Kubernetes manifests, Helm charts, and similar formats let infrastructure be defined, versioned, and reviewed just like application code. But they also introduce a new class of security risk: configuration errors that expose infrastructure to attack before a single line of application code runs.</p>

<p>DryRun Security scans IaC configurations on every pull request, identifying misconfigurations and risks that could lead to data exposure, privilege escalation, or infrastructure compromise.</p>

<h2 id="supported-formats">Supported IaC Formats</h2>

<p>DryRun Security's IaC scanning supports the most widely used infrastructure definition formats:</p>

<ul>
  <li><strong>Terraform</strong> - <code>.tf</code> files for any provider (AWS, GCP, Azure, and others)</li>
  <li><strong>AWS CloudFormation</strong> - JSON and YAML templates</li>
  <li><strong>Kubernetes</strong> - Deployment, Service, Ingress, RBAC, and other resource manifests</li>
  <li><strong>Helm</strong> - Chart templates and values files</li>
  <li><strong>Docker and Docker Compose</strong> - Dockerfile and compose configuration</li>
  <li><strong>GitHub Actions</strong> - Workflow YAML files</li>
</ul>

<h2 id="what-iac-scanning-catches">What IaC Scanning Catches</h2>

<p>DryRun Security's IaC analysis goes beyond generic misconfiguration detection. Common findings include:</p>

<ul>
  <li><strong>Subdomain takeover</strong> - Dangling DNS records or CDN configurations that could be claimed by an attacker to serve malicious content under your domain</li>
  <li><strong>Excessive IAM permissions</strong> - Roles and policies granting broader access than the service requires, violating least privilege</li>
  <li><strong>Public storage buckets</strong> - S3 buckets, GCS buckets, or blob storage containers with unrestricted public access</li>
  <li><strong>Insecure network configurations</strong> - Security groups or firewall rules that expose services to the public internet unnecessarily</li>
  <li><strong>Unencrypted data stores</strong> - Database instances, file systems, or volumes without encryption at rest</li>
  <li><strong>Missing logging and monitoring</strong> - Resources lacking audit trails or access logging</li>
  <li><strong>Container misconfigurations</strong> - Containers running as root, privilege escalation enabled, or with overly broad capabilities</li>
</ul>

<h2 id="contextual-iac-analysis">Contextual IaC Analysis</h2>

<p>Like all DryRun Security analysis, IaC scanning is contextual. A finding is evaluated against the full intent of the infrastructure change - an intentionally public static asset bucket is treated differently from an accidentally public database. When your team uses <a href="../repository-context.html">AGENTS.md</a> to document known-safe infrastructure patterns, DryRun Security's agents apply that context during analysis to reduce false positives.</p>
''',
}

PAGES['sca'] = {
    'title': 'SCA',
    'description': 'Dependency scanning and supply chain risk detection - find vulnerable third-party packages before they reach production.',
    'section': 'Scanning',
    'content': '''
<h2 id="what-is-sca">What Is Software Composition Analysis?</h2>

<p>Modern applications are built on a foundation of open-source libraries and third-party packages. The majority of code in any production service is not written by your team - it comes from the open-source ecosystem. Software Composition Analysis (SCA) is the practice of identifying what third-party components you depend on and whether any of them carry known security vulnerabilities.</p>

<p>DryRun Security's SCA capability analyzes your dependency manifests and lock files on every pull request, detecting when a new or updated dependency introduces a known vulnerability. Because this analysis runs at the PR level, you catch supply chain risk at the moment it enters the codebase - not in a weekly report after it's already in production.</p>

<h2 id="dependency-scanning">Dependency Scanning</h2>

<p>DryRun Security scans package manifests and lock files across all major ecosystems, including:</p>

<ul>
  <li><strong>JavaScript / Node.js</strong> - <code>package.json</code>, <code>package-lock.json</code>, <code>yarn.lock</code></li>
  <li><strong>Python</strong> - <code>requirements.txt</code>, <code>Pipfile</code>, <code>pyproject.toml</code>, <code>poetry.lock</code></li>
  <li><strong>Ruby</strong> - <code>Gemfile</code>, <code>Gemfile.lock</code></li>
  <li><strong>Java / Kotlin</strong> - <code>pom.xml</code>, Gradle build files</li>
  <li><strong>Go</strong> - <code>go.mod</code>, <code>go.sum</code></li>
  <li><strong>Rust</strong> - <code>Cargo.toml</code>, <code>Cargo.lock</code></li>
  <li><strong>.NET</strong> - <code>*.csproj</code>, <code>packages.config</code></li>
</ul>

<h2 id="supply-chain-risk">Supply Chain Risk Detection</h2>

<p>Beyond CVE matching, DryRun Security's contextual analysis evaluates how a vulnerable dependency is actually used in your code. A vulnerable function in a library you only use for unrelated functionality presents a very different risk profile than one you call directly with user-supplied input. This context-aware severity assessment means your team can prioritize remediation based on actual exploitability rather than CVSS scores alone.</p>

<h2 id="vulnerable-dependency-findings">Vulnerable Dependency Findings</h2>

<p>When a vulnerable dependency is detected, DryRun Security posts a finding in the PR that includes the affected package, the specific CVE or vulnerability identifier, the severity, the affected version range, and a recommended remediation (typically a version upgrade). Findings appear in both the PR comment and the GitHub Checks area, and are tracked in the <a href="../risk-register.html">Risk Register</a> for centralized triage.</p>

<h2 id="deepscan-sca">SCA in DeepScan</h2>

<p>DryRun Security now surfaces SCA findings during <a href="../docs/deepscan.html">DeepScan</a> repository analysis, not just during PR reviews. When a DeepScan runs, it identifies vulnerable dependencies across the entire codebase and ingests them as findings. These findings can be filtered by the SCA agent type in the <a href="../docs/risk-register.html">Risk Register</a>, making it easy to isolate dependency-related risk from code-level findings.</p>

<h2 id="sbom-integration">SBOM Integration</h2>

<p>DryRun Security's dependency analysis feeds into SBOM (Software Bill of Materials) generation, enabling you to produce a complete inventory of your software dependencies for compliance and audit purposes. See <a href="../compliance-grc.html">SBOM Generation</a> for details.</p>
''',
}

PAGES['auto-fix'] = {
    'title': 'Auto Fix',
    'description': 'Automated remediation guidance and fix verification for security findings.',
    'section': 'Scanning',
    'content': '''
<h2 id="remediation-guidance">Remediation Guidance</h2>


<h2 id="philosophy">Remediation, Not Auto-Fix</h2>

<p class="lead">DryRun Security does not auto-fix your code. Instead, it provides rich remediation guidance designed to empower the coding and generation agents you already use - Cursor, Claude Code, GitHub Copilot, and others - to fix issues with full context and understanding.</p>

<p>This is a deliberate philosophical choice. Your coding agents have the deepest context about your codebase and the work being performed. They understand your architecture, your patterns, and your intent. DryRun Security's role is to identify the security problem, explain it clearly, and give your agents everything they need to resolve it correctly - not to layer in generated code from a scanner that lacks that context.</p>

<div class="callout callout-info">
<p><strong>Why this matters:</strong> Auto-fix tools risk introducing new problems because they lack the full architectural context of your codebase. By providing guidance rather than generated patches, DryRun Security keeps code generation where it belongs - with the agents and developers who understand the code best.</p>
</div>

<h2 id="what-dryrun-provides">What DryRun Security Provides</h2>

<p>When DryRun Security identifies a vulnerability, the finding includes detailed remediation guidance:</p>

<ul>
  <li><strong>Specific code examples</strong> - Concrete lines of code showing what the fix looks like, tailored to your codebase's frameworks and patterns</li>
  <li><strong>Root cause explanation</strong> - A clear explanation of why the code is vulnerable, so your coding agent understands the underlying problem</li>
  <li><strong>Remediation approach</strong> - Step-by-step guidance on how to address the vulnerability, including considerations for edge cases</li>
  <li><strong>Security context</strong> - The vulnerability class, severity, and any relevant CWE references to help prioritize the fix</li>
</ul>

<h2 id="contextual-guidance">Guidance That Matches Your Code</h2>

<p>Remediation guidance is generated in the context of your specific codebase - not from generic templates. The guidance considers:</p>

<ul>
  <li>The frameworks, libraries, and language idioms your code uses</li>
  <li>The existing patterns in your codebase for similar problems (if you validate input one way elsewhere, the guidance follows the same pattern)</li>
  <li>The surrounding code structure and dependencies that a fix must integrate with</li>
  <li>Security best practices for the specific vulnerability class</li>
</ul>

<p>The result is guidance that a developer or coding agent can act on with confidence - not a generic "sanitize this input" suggestion that still requires significant interpretation.</p>

<h2 id="designed-for-coding-agents">Designed for Coding Agents</h2>

<p>DryRun Security's remediation guidance is structured so that AI coding agents can consume it directly. When a finding with remediation guidance is surfaced in a PR comment, your coding agent can:</p>

<ol>
  <li>Read the vulnerability description and understand the security issue</li>
  <li>Review the code examples and remediation approach</li>
  <li>Apply the fix using its own understanding of your codebase context</li>
  <li>Push the update, which DryRun Security will re-analyze to verify the fix (see <a href="./auto-fix.html">Fix Verification</a>)</li>
</ol>

<p>This workflow keeps the security scanner and the code generator in their respective strengths: DryRun Security excels at finding and explaining vulnerabilities, and your coding agent excels at writing code that fits your codebase.</p>

<h2 id="where-guidance-appears">Where Guidance Appears</h2>

<p>Remediation guidance is presented alongside findings in multiple places:</p>

<ul>
  <li><strong>PR comments</strong> - Inline with each finding in the DryRun Security summary comment</li>
  <li><strong>GitHub Checks</strong> - In the detailed check output for each finding</li>
  <li><strong>Risk Register</strong> - In the finding detail view in the DryRun Security dashboard</li>
  <li><strong>AI Coding Integrations</strong> - Through the DryRun Remediation Skill for Claude Code and other MCP-compatible agents</li>
</ul>



<h2 id="fix-verification">Fix Verification</h2>

<h2 id="closing-the-loop">Closing the Loop</h2>

<p>Applying a security fix and declaring the vulnerability resolved are not the same thing. Fixes can be incomplete, introduce new vulnerabilities, or address the symptoms of a problem without fixing the root cause. Manual verification is time-consuming, and in fast-moving development environments it often doesn't happen at all - the fix gets pushed and the team moves on.</p>

<p>DryRun Security's <strong>Fix Verification</strong> capability closes this loop automatically. When a developer applies a fix to a vulnerability finding and pushes an updated commit, DryRun Security re-runs analysis on the affected code to verify the outcome.</p>

<h2 id="what-verification-checks">What Verification Checks</h2>

<p>Fix Verification performs a targeted re-analysis focused on three questions:</p>

<ol>
  <li><strong>Is the original vulnerability resolved?</strong> - The specific finding that prompted the fix is re-evaluated to confirm the vulnerability no longer exists in the updated code.</li>
  <li><strong>Are there related vulnerabilities?</strong> - The fix's broader impact on the code path is analyzed to ensure the remediation didn't leave related issues unaddressed.</li>
  <li><strong>Did the fix introduce new issues?</strong> - The changed code is scanned for any new vulnerabilities or security anti-patterns introduced by the fix itself.</li>
</ol>

<h2 id="verification-results">Verification Results</h2>

<p>Verification results appear in the updated PR comment and in the DryRun Security dashboard. A successfully verified fix closes the finding in the Risk Register. If verification identifies that the fix is incomplete or has introduced a new issue, a new finding is raised with specific details about what needs to be addressed.</p>

<h2 id="why-this-matters">Why This Matters</h2>

<p>Fix Verification turns security remediation into a closed-loop process. Developers know whether their fix actually worked. Security teams have confidence that closed findings are genuinely closed. And the organization builds a track record of verified remediations rather than a list of acknowledged findings with unknown resolution status.</p>

<p>This is particularly valuable for compliance purposes, where demonstrating that identified vulnerabilities were genuinely remediated - not just acknowledged - is often required.</p>
''',
}


# -- Code Security Intelligence --

PAGES['feature-ships'] = {
    'title': 'Feature Ships',
    'description': 'Track and review features shipped across your codebase using DryRun Security\'s intelligence index.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>Every pull request DryRun Security reviews contributes to an intelligence index - a structured, queryable record of what changed, why it matters, and what security implications it carries. The Feature Ships page explains how to use this index to track and review features as they are shipped across your repositories.</p>

<h2 id="how-it-works">How It Works</h2>

<p>During PR and repository scanning, DryRun Security&rsquo;s models analyze code changes to identify feature-level context: new endpoints, new user flows, new capabilities, and new integrations. These observations are indexed and made available for querying through the <strong>DryRun AI Assistant</strong> on the Insights page and programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>Rather than manually tracking feature releases across PRs, teams can query the intelligence index to get a consolidated view of what shipped, when, and what the security implications are.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;What features shipped this sprint?&rdquo;</strong> - Returns a summary of new capabilities introduced across all monitored repositories.</li>
  <li><strong>&ldquo;Show me the top 5 features we shipped this month with the most risky security implications. Link me to the PRs.&rdquo;</strong> - Surfaces features ranked by security risk with direct PR links.</li>
  <li><strong>&ldquo;Did we ship any new payment flows this quarter?&rdquo;</strong> - Filters the index for domain-specific feature patterns.</li>
  <li><strong>&ldquo;Which repos had the most feature activity last week?&rdquo;</strong> - Identifies the most active areas of development.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Feature ship tracking integrates with DryRun Security&rsquo;s broader analysis. Each feature identified in the index is annotated with:</p>

<ul>
  <li>Security findings from the PR reviews that introduced it</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Sprint reviews</strong> - Generate a security-aware summary of what your team shipped.</li>
  <li><strong>Release readiness</strong> - Verify that all features in a release have been security-reviewed.</li>
  <li><strong>Audit evidence</strong> - Provide auditors with a record of features shipped alongside their security assessments. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['architecture-risks'] = {
    'title': 'Architecture Risks',
    'description': 'Identify and investigate architectural security risks by querying DryRun Security\'s intelligence index.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>Architectural security risks - the kind that emerge from how components interact rather than from individual code flaws - are notoriously hard to detect with traditional tools. DryRun Security&rsquo;s intelligence index captures architectural patterns and changes as they occur across your codebase, making them queryable as a use case through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone product page or dashboard. It is a query pattern - a way to ask DryRun Security&rsquo;s LLM about architectural risks using the structured findings and insights generated from every PR review and <a href="../docs/deepscan.html">DeepScan</a>.</p>

<h2 id="how-it-works">How It Works</h2>

<p>During every PR review and repository scan, DryRun Security&rsquo;s models observe architectural signals: new service boundaries, authentication pattern changes, data flow modifications, infrastructure-as-code updates, and dependency relationship shifts. These observations accumulate in the intelligence index, building a persistent map of your system&rsquo;s architecture and how it evolves over time.</p>

<p>When you query for architecture risks, the LLM has access to the full history of these observations and can surface risks that are invisible at the individual PR level but become apparent when viewed across the full codebase.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;What IAM policy changes were introduced across all repos this quarter?&rdquo;</strong> - Surfaces infrastructure-level permission changes.</li>
  <li><strong>&ldquo;Show me new service-to-service communication paths added this month&rdquo;</strong> - Maps architectural expansion.</li>
  <li><strong>&ldquo;Which repos introduced new external API integrations?&rdquo;</strong> - Identifies new trust boundaries.</li>
  <li><strong>&ldquo;Are there any new unauthenticated endpoints?&rdquo;</strong> - Flags architectural gaps in access control.</li>
</ul>

<h2 id="risk-patterns">Risk Patterns Detected</h2>

<p>The intelligence index tracks architectural risk patterns including:</p>

<ul>
  <li><strong>Trust boundary changes</strong> - New external integrations, API surface expansion, or cross-service data flows.</li>
  <li><strong>Authentication and authorization drift</strong> - Changes to auth patterns that may weaken access control.</li>
  <li><strong>Data flow modifications</strong> - New paths for sensitive data that may bypass existing controls.</li>
  <li><strong>Infrastructure changes</strong> - IaC modifications that alter network topology, permissions, or deployment configuration.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Architecture risk queries integrate with DryRun Security&rsquo;s broader analysis. Each risk pattern identified in the index is annotated with:</p>

<ul>
  <li>Security findings from the PR reviews that introduced the change</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Threat modeling</strong> - Use the intelligence index to feed threat modeling exercises with real, current architectural data.</li>
  <li><strong>Architecture review</strong> - Query for structural changes before approving major releases.</li>
  <li><strong>Compliance</strong> - Demonstrate architectural governance by showing how structural changes are tracked and reviewed. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['developer-trends'] = {
    'title': 'Developer Trends',
    'description': 'Analyze developer behavior and security trend patterns by querying DryRun Security\'s intelligence index.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>Understanding how your team&rsquo;s security practices evolve over time requires more than point-in-time snapshots. DryRun Security&rsquo;s intelligence index captures developer activity patterns as a byproduct of every PR review and <a href="../docs/deepscan.html">DeepScan</a>, making them queryable as a use case through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone dashboard or report. It is a query pattern - a way to ask DryRun Security&rsquo;s LLM about development trends using the structured findings and insights generated across your repositories.</p>

<h2 id="how-it-works">How It Works</h2>

<p>As DryRun Security reviews pull requests, the models record patterns at the contributor level: which types of findings are most common, how quickly findings are addressed, what categories of code changes are being made, and how security posture trends over time. This data is aggregated and anonymizable, designed to improve team processes rather than single out individuals.</p>

<p>When you query for developer trends, the LLM has access to this full history and can identify patterns, inflection points, and areas where additional attention may help.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;What are the most common security findings across our team this month?&rdquo;</strong> - Identifies patterns that may indicate a training opportunity.</li>
  <li><strong>&ldquo;How has our mean time to remediate findings changed over the last quarter?&rdquo;</strong> - Tracks security responsiveness trends.</li>
  <li><strong>&ldquo;Which repositories have the highest density of new findings?&rdquo;</strong> - Highlights areas under active development that may need more review.</li>
  <li><strong>&ldquo;Show me a chart of finding categories over the past 6 months&rdquo;</strong> - Visualizes how the types of issues are shifting.</li>
</ul>

<h2 id="trend-categories">Trend Categories</h2>

<p>The intelligence index tracks several dimensions of developer activity:</p>

<ul>
  <li><strong>Finding frequency and type</strong> - What categories of security issues appear most often and whether they are increasing or decreasing.</li>
  <li><strong>Remediation velocity</strong> - How quickly findings are addressed after detection.</li>
  <li><strong>Code change patterns</strong> - Volume and nature of changes across repositories, highlighting areas of high activity.</li>
  <li><strong>Policy compliance</strong> - How often <a href="../docs/custom-code-policies.html">Custom Code Policies</a> are triggered and resolved.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Developer trend queries integrate with DryRun Security&rsquo;s broader analysis. Each trend identified in the index is annotated with:</p>

<ul>
  <li>Security findings from the PR reviews that drive the trend</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Security training prioritization</strong> - Focus training on the finding categories that appear most frequently.</li>
  <li><strong>Process improvement</strong> - Track whether process changes (e.g., new policies, new tools) are having the intended effect.</li>
  <li><strong>Management reporting</strong> - Generate trend data for leadership reviews and board reporting.</li>
</ul>
''',
}

PAGES['incident-response'] = {
    'title': 'Incident Response Investigation',
    'description': 'Investigate security incidents by querying DryRun Security\'s intelligence index for code change history and findings.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>When a security incident occurs, speed of investigation is critical. DryRun Security&rsquo;s intelligence index provides a queryable record of every code change, security finding, and policy evaluation across your repositories - enabling rapid, targeted investigation through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone incident response tool. It is a query pattern - a way to ask DryRun Security&rsquo;s LLM to trace code changes, findings, and triage decisions using the structured insights generated from every PR review and <a href="../docs/deepscan.html">DeepScan</a>.</p>

<h2 id="how-it-works">How It Works</h2>

<p>Every PR review and repository scan feeds the intelligence index with structured data: what changed, what was found, which policies were evaluated, and what the security assessment was. During incident response, this index becomes an investigation tool. Instead of piecing together information from Git logs, CI systems, and security dashboards, responders can query the LLM directly - and it has access to the full history of findings and insights across your organization.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;Which PR introduced the risky dependency?&rdquo;</strong> - Traces a vulnerable component back to its introduction.</li>
  <li><strong>&ldquo;Show me all changes to authentication code in the last 30 days&rdquo;</strong> - Scopes investigation to security-critical areas.</li>
  <li><strong>&ldquo;What secrets-related findings were suppressed in repo X?&rdquo;</strong> - Reviews triage decisions that may be relevant to the incident.</li>
  <li><strong>&ldquo;List all PRs that modified payment processing logic this quarter&rdquo;</strong> - Narrows investigation to a specific functional area.</li>
</ul>

<h2 id="investigation-capabilities">Investigation Capabilities</h2>

<p>The intelligence index supports incident response workflows including:</p>

<ul>
  <li><strong>Change tracing</strong> - Identify exactly which PR introduced a specific change, dependency, or configuration.</li>
  <li><strong>Blast radius assessment</strong> - Determine what other components or repositories may be affected by the same issue.</li>
  <li><strong>Timeline reconstruction</strong> - Build a chronological view of security-relevant changes leading up to an incident.</li>
  <li><strong>Finding review</strong> - Surface any prior findings related to the affected code that may have been triaged or deferred.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Incident response queries integrate with DryRun Security&rsquo;s broader analysis. Each investigation query draws on:</p>

<ul>
  <li>Security findings from the PR reviews across your repositories</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Vulnerability triage</strong> - When a CVE is disclosed, quickly determine if and where the affected component exists in your codebase.</li>
  <li><strong>Breach investigation</strong> - Trace the code path involved in a security breach back through its development history.</li>
  <li><strong>Post-incident review</strong> - Generate a comprehensive timeline of changes for post-mortem analysis. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a> for audit trail documentation.</li>
</ul>
''',
}

PAGES['shadow-ai'] = {
    'title': 'Shadow AI',
    'description': 'Detect and investigate unauthorized AI tool usage by querying DryRun Security\'s intelligence index.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>Shadow AI refers to the use of AI coding tools, models, or AI-generated code that is not sanctioned or tracked by the organization. DryRun Security&rsquo;s intelligence index captures signals of AI involvement during every PR review and <a href="../docs/deepscan.html">DeepScan</a>, making them queryable as a use case through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone detection dashboard. It is a query pattern - a way to ask DryRun Security&rsquo;s LLM about AI usage patterns using the structured findings and insights generated across your repositories.</p>

<h2 id="how-it-works">How It Works</h2>

<p>DryRun Security&rsquo;s models analyze code changes for indicators of AI-generated or AI-assisted code. These signals - including coding patterns, commit metadata, and structural characteristics - are indexed alongside all other findings. When you query for shadow AI patterns, the LLM has access to the full history of these observations and can investigate where AI tools are being used, whether that usage aligns with organizational policy, and what security implications it carries.</p>

<p>This capability builds on DryRun Security&rsquo;s <a href="../docs/ai-coding-integration.html">AI Coding Integration</a> analysis, extending it into the intelligence index for historical querying and trend analysis.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;Show me PRs with AI-generated code indicators this month&rdquo;</strong> - Surfaces pull requests where AI involvement was detected.</li>
  <li><strong>&ldquo;Which repositories have the highest percentage of AI-assisted contributions?&rdquo;</strong> - Identifies where AI tools are most actively used.</li>
  <li><strong>&ldquo;Are there AI-generated code patterns in security-critical paths?&rdquo;</strong> - Focuses investigation on high-risk areas.</li>
  <li><strong>&ldquo;What AI coding tools are being used across our organization?&rdquo;</strong> - Maps the AI tool landscape in your development workflow.</li>
</ul>

<h2 id="detection-signals">Detection Signals</h2>

<p>The intelligence index tracks multiple dimensions of AI involvement:</p>

<ul>
  <li><strong>Code pattern analysis</strong> - Structural and stylistic indicators that suggest AI generation.</li>
  <li><strong>Commit metadata</strong> - Signals from commit messages, authorship patterns, and contribution timing.</li>
  <li><strong>Tool fingerprints</strong> - Identifiable patterns associated with specific AI coding assistants.</li>
  <li><strong>Volume anomalies</strong> - Unusual spikes in code contribution volume that may indicate AI-assisted development.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Shadow AI queries integrate with DryRun Security&rsquo;s broader analysis. Each AI-related observation in the index is annotated with:</p>

<ul>
  <li>Security findings from the PR reviews that flagged AI indicators</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Policy enforcement</strong> - Verify that AI tool usage complies with organizational policies. Use <a href="../docs/custom-code-policies.html">Custom Code Policies</a> to enforce AI-specific rules.</li>
  <li><strong>Risk assessment</strong> - Evaluate the security implications of AI-generated code in your codebase.</li>
  <li><strong>Governance reporting</strong> - Provide leadership with visibility into AI adoption patterns across engineering teams.</li>
  <li><strong>Compliance</strong> - Document AI usage for regulatory requirements. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['security-review-requests'] = {
    'title': 'New Feature or Repository Security Review',
    'description': 'Request security reviews for new features or repositories by querying DryRun Security\'s intelligence index.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>When a new feature is proposed or a new repository is onboarded, security teams need to quickly assess the risk landscape. DryRun Security&rsquo;s intelligence index provides the foundation for these reviews - enabling teams to query historical patterns, similar implementations, and known risks through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone review tool. It is a query pattern - a way to ask DryRun Security&rsquo;s LLM to assess new features or repositories using the structured findings and insights generated from every PR review and <a href="../docs/deepscan.html">DeepScan</a> across your organization.</p>

<h2 id="how-it-works">How It Works</h2>

<p>The intelligence index accumulated from PR and repository scanning contains a structured record of security patterns across your entire codebase. When reviewing a new feature or repository, you query the LLM to find relevant precedents: how similar features were implemented elsewhere, what security issues arose, and what patterns to watch for. The LLM has access to all findings details and insights generated across your repositories.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;What security findings were associated with our last payment integration?&rdquo;</strong> - Reviews precedent for a similar new feature.</li>
  <li><strong>&ldquo;Summarize the security posture of repo X&rdquo;</strong> - Gets a baseline assessment for a repository under review.</li>
  <li><strong>&ldquo;What are the most common vulnerabilities in our Go services?&rdquo;</strong> - Informs a review of a new Go repository.</li>
  <li><strong>&ldquo;Show me all findings related to file upload handling across our repos&rdquo;</strong> - Gathers intelligence before reviewing a new file upload feature.</li>
</ul>

<h2 id="review-workflow">Review Workflow</h2>

<p>The intelligence index supports a structured security review process:</p>

<ul>
  <li><strong>Precedent search</strong> - Query for similar features or patterns across your codebase to understand what risks to expect.</li>
  <li><strong>Risk baseline</strong> - For new repositories, query the index for common finding categories in similar technology stacks.</li>
  <li><strong>Policy alignment</strong> - Verify that appropriate <a href="../docs/custom-code-policies.html">Custom Code Policies</a> are configured for the new feature or repository.</li>
  <li><strong>Ongoing monitoring</strong> - After the review, the intelligence index continues to track the feature or repository as it evolves.</li>
</ul>

<h2 id="security-review-integration">Security Review Integration</h2>

<p>Security review queries integrate with DryRun Security&rsquo;s broader analysis. Each query draws on:</p>

<ul>
  <li>Security findings from the PR reviews across your repositories</li>
  <li>Risk severity assessment from the <a href="../docs/risk-register.html">Risk Register</a></li>
  <li>Policy evaluation results from <a href="../docs/custom-code-policies.html">Custom Code Policies</a></li>
  <li>Links to the originating PRs for full context</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>New feature design review</strong> - Before implementation begins, query the index to inform the security architecture.</li>
  <li><strong>Repository onboarding</strong> - When adding a new repository to DryRun Security, use the index to benchmark against similar repos.</li>
  <li><strong>Acquisition due diligence</strong> - Assess acquired codebases by querying the index for risk patterns after initial scanning.</li>
  <li><strong>Compliance pre-checks</strong> - Verify that new features meet regulatory requirements before they ship. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['security-reviews'] = {
    'title': 'Security Reviews',
    'description': 'Query DryRun Security\'s intelligence index for contextual security analysis, business logic detection, and model verification insights.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>DryRun Security&rsquo;s intelligence index captures deep security analysis from every PR review and <a href="../docs/deepscan.html">DeepScan</a> - including contextual security analysis, business logic detection, and model-independent verification results. These insights are queryable as use cases through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone product page. It describes the analytical capabilities that power the intelligence index and how to query for their results. Every query to the LLM draws on the full depth of these analytical methods.</p>

<h2 id="contextual-analysis">Contextual Security Analysis</h2>

<h3 id="the-limits-of-pattern-matching">The Limits of Pattern Matching</h3>

<p>Pattern-matching SAST tools work by detecting syntactic patterns associated with known vulnerability classes. If you call <code>execute_query</code> with a string that contains user input, you get flagged. If you use an outdated encryption algorithm, you get flagged. The pattern is present; the finding is generated.</p>

<p>The fundamental problem is that security in real code is almost never a matter of syntactic patterns. Whether a SQL query is vulnerable depends on how the input was validated before it arrived. Whether a redirect is dangerous depends on whether the target URL can be influenced by an attacker. Whether an API endpoint is a risk depends on whether authorization is enforced - which might happen in middleware the pattern matcher never examined.</p>

<p>This is why traditional SAST produces so many false positives (flagging safe code) and so many false negatives (missing real vulnerabilities that don't match a pattern). It isn't a tuning problem. It's a fundamental limitation of the approach.</p>

<h3 id="what-full-context-means">What "Full Context" Means</h3>

<p>DryRun Security's Contextual Security Analysis evaluates code through several dimensions of context simultaneously:</p>

<ul>
  <li><strong>Code patterns and data flow</strong> - Traces the flow of data from its origin through transformations and into sensitive operations. A function that receives a validated, sanitized parameter is treated differently from one that receives a raw request field.</li>
  <li><strong>Runtime behaviors</strong> - Considers the runtime context: which framework is in use, how middleware is configured, what the deployment topology implies about trust boundaries.</li>
  <li><strong>Developer intent</strong> - Evaluates what a code change is trying to accomplish. A change that adds a new authenticated API endpoint has very different security implications from a change that modifies how authentication is enforced.</li>
  <li><strong>Cross-file analysis</strong> - Follows vulnerability chains across file boundaries, providing the comprehensive view that single-file analysis fundamentally cannot.</li>
</ul>

<h3 id="example-queries-csa">Example Queries</h3>

<ul>
  <li><strong>&ldquo;Which PRs had findings that required cross-file analysis to detect?&rdquo;</strong> - Surfaces complex vulnerabilities that pattern matchers would miss.</li>
  <li><strong>&ldquo;Show me findings where context changed the severity assessment&rdquo;</strong> - Highlights where contextual analysis made a material difference.</li>
  <li><strong>&ldquo;What percentage of our findings this month were business logic flaws?&rdquo;</strong> - Measures coverage beyond pattern-matching categories.</li>
</ul>

<h2 id="business-logic">Business Logic Detection</h2>

<h3 id="what-are-business-logic-flaws">What Are Business Logic Flaws?</h3>

<p>Business logic flaws are vulnerabilities that arise from errors in how an application implements its intended behavior - not from missing input validation or insecure library calls, but from flawed assumptions in the logic itself. No pattern matcher can find these. They require understanding what the code is supposed to do - and then evaluating whether it actually does it securely.</p>

<h3 id="examples-of-what-it-catches">Examples of What It Catches</h3>

<ul>
  <li><strong>IDOR (Insecure Direct Object Reference)</strong> - An API endpoint that looks up a resource by user-controlled ID without verifying the requesting user owns that resource.</li>
  <li><strong>Race conditions in transactions</strong> - Logic that allows a resource to be consumed multiple times if requests arrive simultaneously.</li>
  <li><strong>Authorization on the wrong layer</strong> - UI-level access controls that aren't enforced at the API layer.</li>
  <li><strong>State machine violations</strong> - Workflows that can be driven into invalid states by skipping or repeating steps.</li>
  <li><strong>Privilege abuse paths</strong> - Sequences of otherwise-legitimate operations that achieve an outcome an attacker shouldn't be able to reach.</li>
</ul>

<h3 id="example-queries-logic">Example Queries</h3>

<ul>
  <li><strong>&ldquo;Show me all business logic findings across our repos this quarter&rdquo;</strong> - Surfaces the category of findings traditional tools miss entirely.</li>
  <li><strong>&ldquo;Which repos have the most IDOR findings?&rdquo;</strong> - Identifies authorization pattern weaknesses by codebase.</li>
  <li><strong>&ldquo;What race condition risks have been flagged in our payment services?&rdquo;</strong> - Focuses on a specific risk class in a critical domain.</li>
</ul>

<h2 id="model-verification">Model-Independent Verification</h2>

<p>DryRun Security's <a href="../docs/pr-variant-analysis.html">multi-agent architecture</a> provides a natural verification layer. When multiple specialized agents analyze the same code from different perspectives - one focused on injection, another on authorization, another on data flow - their findings serve as cross-checks on each other. The combination of AI-powered contextual analysis and deterministic validation (CVE lookups, secrets format checks, IaC specification matching) produces findings that are both contextually relevant and factually grounded.</p>

<h3 id="example-queries-verification">Example Queries</h3>

<ul>
  <li><strong>&ldquo;How consistent are our findings across repeated scans?&rdquo;</strong> - Evaluates reliability of the multi-agent verification process.</li>
  <li><strong>&ldquo;Which findings were confirmed by multiple agents?&rdquo;</strong> - Surfaces high-confidence results validated through cross-checking.</li>
</ul>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Deep finding investigation</strong> - Query the index to understand the full context behind any finding - what analysis methods detected it and why.</li>
  <li><strong>Coverage assessment</strong> - Evaluate what categories of vulnerabilities your scans are catching beyond what pattern matchers detect.</li>
  <li><strong>Audit evidence</strong> - Demonstrate the depth and rigor of your security analysis methodology. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['pr-variant-analysis'] = {
    'title': 'PR Variant Analysis',
    'description': 'Query DryRun Security\'s intelligence index for behavioral analysis, multi-agent PR review results, and specialized analyzer findings.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>AppSec engineers can perform variant analysis using DryRun Security&rsquo;s Insights capabilities. To get started:</p>

<ol>
  <li>Go to the <strong>Insights</strong> tab in the DryRun Security Dashboard.</li>
  <li>Look at a finding on the page and click <strong>&ldquo;Investigate&rdquo;</strong>.</li>
  <li>This loads the appropriate question into the AI assistant, where you can then interact with the Insights LLM to explore the finding further.</li>
</ol>

<h2 id="example-queries">Example Queries</h2>

<ol>
  <li>What are the security implications of this change?</li>
  <li>Are there any potential vulnerabilities introduced?</li>
  <li>What sensitive data or permissions might be affected?</li>
  <li>Any recommendations for improving the security posture?</li>
  <li>Have any similar issues been seen before?</li>
</ol>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Targeted investigation</strong> - Use the <strong>Investigate PR</strong> action from the Insights page to run a deep variant analysis on any specific pull request.</li>
  <li><strong>Analyzer performance</strong> - Query findings by analyzer to understand which vulnerability classes are most active in your codebase.</li>
  <li><strong>Audit evidence</strong> - Demonstrate the depth and rigor of multi-agent analysis for compliance purposes. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['vulnerability-trends'] = {
    'title': 'Vulnerability Trends',
    'description': 'Query DryRun Security\'s intelligence index for vulnerability coverage, risk trends, and the full coverage matrix.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>DryRun Security builds and maintains a continuous security baseline across every connected repository. The intelligence index captures vulnerability trends, coverage data, and risk trajectories from every PR review and <a href="../docs/deepscan.html">DeepScan</a> - making them queryable as use cases through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>This is not a standalone dashboard. It describes queryable use cases for understanding how your vulnerability landscape is evolving and what DryRun Security covers.</p>

<h2 id="risk-trending">Risk Trending</h2>

<h3 id="continuous-security-baseline">Continuous Security Baseline</h3>

<p>As scans run - on each pull request and each DeepScan - findings are recorded and trend data is updated. This creates a running picture of security posture that you can query at any level of granularity: the full organization, a specific team, a single repository, or a particular vulnerability class.</p>

<h3 id="comparing-periods">Comparing Periods</h3>

<p>Risk trending queries allow you to compare any two time periods. Common comparisons include:</p>

<ul>
  <li><strong>Week over week</strong> - Are you introducing new findings faster than you're closing old ones?</li>
  <li><strong>Sprint over sprint</strong> - Are security remediation efforts keeping pace with development velocity?</li>
  <li><strong>Quarter over quarter</strong> - Is the security program producing measurable improvement?</li>
  <li><strong>Before and after an initiative</strong> - Did the shift-left push or the new policy configuration actually change outcomes?</li>
</ul>

<h3 id="example-queries-trending">Example Queries</h3>

<ul>
  <li><strong>&ldquo;How has our critical finding count changed over the last quarter?&rdquo;</strong> - Tracks risk trajectory over time.</li>
  <li><strong>&ldquo;Which repos showed the biggest increase in findings this month?&rdquo;</strong> - Identifies regression hotspots.</li>
  <li><strong>&ldquo;Compare our finding rates before and after we enabled Custom Code Policies&rdquo;</strong> - Measures the impact of a security initiative.</li>
</ul>

<h2 id="vulnerability-coverage">Vulnerability Coverage</h2>

<h3 id="coverage-overview">Coverage Overview</h3>

<p>DryRun Security detects vulnerabilities across a broad spectrum of security categories. Unlike pattern-matching tools that rely on a fixed database of known-bad code patterns, DryRun's <a href="../docs/security-reviews.html">Contextual Security Analysis</a> evaluates code in context - tracing data flows, reasoning about authorization logic, and assessing exploitability. This means coverage extends beyond what signature-based tools can detect.</p>

<h3 id="owasp-top-10">OWASP Top 10 Coverage</h3>

<div class="table-wrap">
<table>
<thead><tr><th>OWASP Category</th><th>DryRun Coverage</th><th>Analyzer</th></tr></thead>
<tbody>
<tr><td>A01: Broken Access Control</td><td>IDOR, missing authorization, privilege escalation</td><td>IDOR Analyzer, GSA</td></tr>
<tr><td>A02: Cryptographic Failures</td><td>Weak algorithms, hardcoded keys, improper TLS</td><td>Secrets Analyzer, GSA</td></tr>
<tr><td>A03: Injection</td><td>SQL injection, command injection, LDAP injection</td><td>SQLi Analyzer, GSA</td></tr>
<tr><td>A04: Insecure Design</td><td>Business logic flaws, missing rate limits, broken auth flows</td><td>GSA, Business Logic Detection</td></tr>
<tr><td>A05: Security Misconfiguration</td><td>Debug artifacts, permissive CORS, unsafe defaults</td><td>GSA, IaC Scanning</td></tr>
<tr><td>A06: Vulnerable Components</td><td>Known CVEs in dependencies, license risks</td><td>SCA</td></tr>
<tr><td>A07: Auth Failures</td><td>Broken authentication, session management issues</td><td>GSA</td></tr>
<tr><td>A08: Data Integrity Failures</td><td>Unsafe deserialization, missing integrity checks</td><td>GSA</td></tr>
<tr><td>A09: Logging Failures</td><td>Missing security logging, leaky error messages</td><td>GSA</td></tr>
<tr><td>A10: SSRF</td><td>Server-side request forgery via user-controlled URLs</td><td>SSRF Analyzer</td></tr>
</tbody>
</table>
</div>

<h3 id="beyond-owasp">Beyond OWASP</h3>

<p>Many real-world vulnerabilities do not fit neatly into the OWASP Top 10. DryRun Security's contextual approach catches classes of issues that pattern-matching tools typically miss entirely:</p>

<ul>
  <li><strong>Business logic flaws</strong> - Authorization bypasses, race conditions, and workflow manipulation that depend on application-specific semantics.</li>
  <li><strong>Mass assignment</strong> - Unsafe binding of user input to internal model fields.</li>
  <li><strong>Cross-site scripting (XSS)</strong> - Including framework-specific pitfalls in templating engines.</li>
  <li><strong>Secrets and credentials</strong> - Distinguished from test fixtures through context analysis.</li>
  <li><strong>Infrastructure as code misconfigurations</strong> - Overly permissive IAM policies, public S3 buckets, missing encryption.</li>
</ul>

<h3 id="example-queries-coverage">Example Queries</h3>

<ul>
  <li><strong>&ldquo;What vulnerability categories are most common in our codebase?&rdquo;</strong> - Maps your actual vulnerability landscape.</li>
  <li><strong>&ldquo;Do we have any OWASP A01 findings open right now?&rdquo;</strong> - Checks coverage against a specific OWASP category.</li>
  <li><strong>&ldquo;Which analyzers are generating the most findings?&rdquo;</strong> - Identifies which vulnerability classes are most active.</li>
</ul>

<h2 id="coverage-matrix">Coverage Matrix</h2>

<p>This table lists the vulnerability categories DryRun Security can detect with the Code Review Agent. CWE mappings are examples to help anchor each category to common weakness definitions.</p>

<h3 id="vulnerability-categories">Vulnerability Categories</h3>

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Description</th>
      <th>Example CWEs</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>API Query Injection</td><td>Improper handling of user-controlled input in API queries that allows attackers to manipulate backend queries or filters.</td><td>CWE-943, CWE-74</td></tr>
    <tr><td>Authentication Bypass</td><td>Flaws that allow users to bypass authentication mechanisms and gain access without valid credentials.</td><td>CWE-287, CWE-306</td></tr>
    <tr><td>Missing Authorization Checks</td><td>Endpoints or functions that fail to enforce authorization, allowing users to access resources they should not.</td><td>CWE-862</td></tr>
    <tr><td>Business Logic Flaw</td><td>Errors in application logic that can be abused to gain unintended outcomes.</td><td>CWE-840</td></tr>
    <tr><td>Cache Poisoning</td><td>Manipulation of cache entries to serve malicious or incorrect content to other users.</td><td>CWE-444, CWE-113</td></tr>
    <tr><td>Configuration Injection</td><td>Injection of untrusted input into configuration files, environment variables, or runtime settings.</td><td>CWE-15, CWE-20</td></tr>
    <tr><td>Cryptographic Weakness</td><td>Use of weak, broken, or outdated cryptographic algorithms, keys, or practices.</td><td>CWE-327, CWE-326</td></tr>
    <tr><td>Cross-Site Request Forgery (CSRF)</td><td>Actions performed on behalf of an authenticated user without their consent.</td><td>CWE-352</td></tr>
    <tr><td>CSV Injection</td><td>Injection of spreadsheet formulas into CSV exports that execute when opened.</td><td>CWE-1236</td></tr>
    <tr><td>Email Header Injection</td><td>Manipulation of email headers through unsanitized input.</td><td>CWE-93</td></tr>
    <tr><td>Excessive Privileges</td><td>Users, services, or tokens granted more permissions than required.</td><td>CWE-250, CWE-269</td></tr>
    <tr><td>Hardcoded Credentials</td><td>Credentials embedded directly in source code.</td><td>CWE-798, CWE-259</td></tr>
    <tr><td>HTTP Header Injection</td><td>Injection of malicious content into HTTP headers.</td><td>CWE-113, CWE-93</td></tr>
    <tr><td>Insecure Direct Object Reference (IDOR)</td><td>Direct access to internal objects using user-controlled identifiers without proper authorization.</td><td>CWE-639, CWE-284</td></tr>
    <tr><td>Information Disclosure</td><td>Exposure of sensitive data such as secrets, internal paths, or stack traces.</td><td>CWE-200, CWE-209</td></tr>
    <tr><td>Insecure Client Storage</td><td>Sensitive data stored insecurely on the client side.</td><td>CWE-922, CWE-312</td></tr>
    <tr><td>Insecure Defaults</td><td>Unsafe default configurations that weaken security.</td><td>CWE-276, CWE-1188</td></tr>
    <tr><td>Insecure Deserialization</td><td>Deserializing untrusted data in a way that allows code execution or data manipulation.</td><td>CWE-502</td></tr>
    <tr><td>Insecure File Upload</td><td>File upload functionality that allows malicious files or unrestricted file types.</td><td>CWE-434</td></tr>
    <tr><td>Insecure Transport</td><td>Use of unencrypted or improperly secured network communication.</td><td>CWE-319, CWE-295</td></tr>
    <tr><td>Intent Redirection</td><td>Unvalidated redirection logic that can send users to unintended destinations.</td><td>CWE-601</td></tr>
    <tr><td>Language Version Risk</td><td>Use of outdated or unsupported programming language versions.</td><td>CWE-1104</td></tr>
    <tr><td>LLM Tool Misuse</td><td>Unsafe use of large language model tools, including insecure prompt handling.</td><td>CWE-20, CWE-74, CWE-1426</td></tr>
    <tr><td>Log Injection</td><td>Injection of untrusted input into logs.</td><td>CWE-117</td></tr>
    <tr><td>Mass Assignment</td><td>Automatic binding of user input to object properties without restricting sensitive fields.</td><td>CWE-915</td></tr>
    <tr><td>Memory Safety Issue</td><td>Unsafe memory operations that can lead to crashes or code execution.</td><td>CWE-119, CWE-787, CWE-416</td></tr>
    <tr><td>Network Exposure</td><td>Unintended exposure of internal services, ports, or network resources.</td><td>CWE-668</td></tr>
    <tr><td>Open CORS Policy</td><td>Overly permissive Cross-Origin Resource Sharing policies.</td><td>CWE-942</td></tr>
    <tr><td>Open Redirect</td><td>Redirects that accept untrusted input, enabling phishing attacks.</td><td>CWE-601</td></tr>
    <tr><td>Path Traversal</td><td>Manipulation of file paths to access files outside the intended scope.</td><td>CWE-22</td></tr>
    <tr><td>Privilege Escalation</td><td>Flaws that allow users to gain higher privileges than intended.</td><td>CWE-269, CWE-284</td></tr>
    <tr><td>Prompt Injection</td><td>Manipulation of LLM prompts that alters behavior or leaks data.</td><td>CWE-77, CWE-74, CWE-913, CWE-1427</td></tr>
    <tr><td>Prototype Pollution</td><td>Modification of object prototypes that can impact application logic.</td><td>CWE-1321</td></tr>
    <tr><td>Remote Code Execution (RCE)</td><td>Flaws that allow attackers to execute arbitrary code on the host system.</td><td>CWE-94, CWE-78</td></tr>
    <tr><td>Resource Exhaustion</td><td>Operations that can consume excessive CPU, memory, or resources.</td><td>CWE-400</td></tr>
    <tr><td>SQL Injection (SQLi)</td><td>Injection of malicious SQL queries through unsanitized input.</td><td>CWE-89</td></tr>
    <tr><td>Server-Side Request Forgery (SSRF)</td><td>Server-side requests to internal or unintended external resources.</td><td>CWE-918</td></tr>
    <tr><td>Subdomain Takeover</td><td>Dangling subdomains that can be claimed by attackers.</td><td>CWE-668, CWE-284</td></tr>
    <tr><td>Supply Chain Risk</td><td>Risks introduced through third-party libraries or dependencies.</td><td>CWE-1104, CWE-829</td></tr>
    <tr><td>Terminal Escape Injection</td><td>Injection of terminal control characters that manipulate terminal output.</td><td>CWE-150, CWE-74</td></tr>
    <tr><td>Time-of-Check Time-of-Use (TOCTOU)</td><td>Race conditions where system state changes between validation and use.</td><td>CWE-367</td></tr>
    <tr><td>Timing Side Channel</td><td>Information leakage through measurable differences in execution time.</td><td>CWE-208</td></tr>
    <tr><td>UI Spoofing</td><td>User interface elements designed to deceive users.</td><td>CWE-451</td></tr>
    <tr><td>User Enumeration</td><td>Ability to determine valid users based on application responses.</td><td>CWE-203, CWE-204</td></tr>
    <tr><td>Vulnerable Dependency</td><td>Use of third-party dependencies with known security vulnerabilities.</td><td>CWE-937, CWE-1104</td></tr>
    <tr><td>XML Injection</td><td>Injection of malicious XML content that alters processing.</td><td>CWE-91</td></tr>
    <tr><td>Cross-Site Scripting (XSS)</td><td>Injection of malicious scripts that execute in a user's browser.</td><td>CWE-79</td></tr>
    <tr><td>XML External Entity (XXE)</td><td>XML parsing vulnerabilities that allow access to internal files or services.</td><td>CWE-611</td></tr>
  </tbody>
</table>
</div>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Risk trending</strong> - Query the index to understand whether your security posture is improving or degrading over time.</li>
  <li><strong>Coverage validation</strong> - Verify that your scans are detecting the vulnerability categories relevant to your technology stack.</li>
  <li><strong>Compliance reporting</strong> - Generate trend data and coverage evidence for auditors and leadership. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}

PAGES['application-summary'] = {
    'title': 'Application Summary',
    'description': 'Query DryRun Security\'s intelligence index for organization-wide security posture, analytics, and repository-level insights.',
    'section': 'Code Security Intelligence',
    'content': '''
<h2 id="overview">Overview</h2>

<p>The DryRun Security Dashboard provides a unified view of your organization's security posture. The intelligence index captures analytics, risk trends, and repository-level insights from every PR review and <a href="../docs/deepscan.html">DeepScan</a> - making them queryable through the <strong>DryRun AI Assistant</strong> on the Insights page or programmatically through the <a href="../docs/mcp.html">MCP Integration</a>.</p>

<p>The dashboard itself supports both strategic and tactical security work. At the strategic level, it provides the trend data and aggregate visibility needed to report to leadership and make prioritization decisions. At the tactical level, it gives engineers and security reviewers the filtered views they need to work through findings efficiently. The queries described below extend this data into a conversational, on-demand interface.</p>

<h2 id="example-queries">Example Queries</h2>

<ul>
  <li><strong>&ldquo;What were the biggest findings last week?&rdquo;</strong> - Surfaces the most significant security issues across your organization.</li>
  <li><strong>&ldquo;Which repos need the most attention right now?&rdquo;</strong> - Identifies repositories with the highest concentration of open findings.</li>
  <li><strong>&ldquo;Show me a chart of risky alerts by repo&rdquo;</strong> - Generates a visual breakdown of risk distribution.</li>
  <li><strong>&ldquo;What percentage of our PRs are being scanned?&rdquo;</strong> - Checks coverage metrics across the organization.</li>
  <li><strong>&ldquo;How has our finding velocity changed this quarter?&rdquo;</strong> - Compares the rate of new findings versus closures over time.</li>
</ul>

<h2 id="analytics-overview">Analytics Overview</h2>

<p>The intelligence index tracks aggregate metrics across your connected repositories, all queryable through natural language:</p>

<ul>
  <li><strong>Total findings</strong> by severity (Critical, High, Medium, Low), with trend lines showing how these numbers have changed over your selected time window</li>
  <li><strong>Finding velocity</strong> - How many new findings are being introduced versus how many are being closed or triaged</li>
  <li><strong>Coverage metrics</strong> - What percentage of PRs across your organization are being scanned, and scan volume over time</li>
  <li><strong>Agent breakdown</strong> - Which security agents are generating the most findings, identifying which vulnerability classes are most prevalent</li>
</ul>

<h2 id="repository-level-insights">Repository-Level Insights</h2>

<p>Drilling down to the repository level, the intelligence index can surface:</p>

<ul>
  <li>Open findings by severity and type</li>
  <li>Recent PR scan history with results</li>
  <li>DeepScan history and current finding baseline</li>
  <li>Risk trend for the repository over time</li>
  <li>Configuration settings currently applied</li>
</ul>

<h2 id="platform-navigation">Platform Navigation</h2>

<p>The DryRun Security dashboard organizes its features in a sidebar with three sections:</p>

<ul>
  <li><strong>Main</strong>
    <ul>
      <li><a href="./risk-register.html">Risk Register</a> - Centralized finding management</li>
      <li>Repositories - Connected repository list and status</li>
      <li>Pull Requests - PR scan history and results</li>
      <li><a href="../docs/deepscan.html">DeepScan</a> - Full-repository security analysis</li>
      <li><a href="../docs/custom-code-policies.html">Code Policies</a> - Custom Code Policy management</li>
      <li><a href="./feature-ships.html">Intelligence Queries</a> <em>(Beta)</em> - AI-powered security Q&amp;A</li>
    </ul>
  </li>
  <li><strong>Settings</strong>
    <ul>
      <li><a href="./pr-scanning-configuration.html">Configurations</a> - Per-repository agent and policy settings</li>
      <li><a href="../docs/slack-integration.html">Integrations</a> - Slack and webhook notification setup</li>
      <li><a href="../docs/dryrun-api.html">Access Keys</a> - API key management</li>
    </ul>
  </li>
  <li><strong>Help</strong>
    <ul>
      <li>Docs - Link to this documentation site</li>
      <li>Ask Questions - Contact DryRun Security support</li>
    </ul>
  </li>
</ul>

<p>A <strong>Dark Mode</strong> toggle at the bottom of the sidebar lets you switch between light and dark themes.</p>

<h2 id="use-cases">Use Cases</h2>

<ul>
  <li><strong>Executive reporting</strong> - Generate on-demand security posture summaries for leadership and board reporting.</li>
  <li><strong>Team standups</strong> - Query for a quick overview of what changed since yesterday across your repositories.</li>
  <li><strong>Audit preparation</strong> - Pull comprehensive security posture data for compliance reviews. See <a href="../docs/compliance-grc.html">Compliance and Audit Readiness</a>.</li>
</ul>
''',
}


# -- Platform --

PAGES['pr-scanning-configuration'] = {
    'title': 'PR Scanning Configuration',
    'description': 'Customize DryRun Security behavior per repository - enable agents, attach policies, configure blocking, and set up notifications.',
    'section': 'Platform',
    'content': '''
<p>Configurations let you customize how DryRun Security behaves for each repository or group of repositories. You can control which agents run, which policies are enforced, whether findings block PRs, and how notifications are delivered.</p>

<h2 id="creating-a-configuration">Creating a Configuration</h2>

<ol>
  <li>Log in to the DryRun Security portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</li>
  <li>Navigate to <strong>Settings &gt; Configurations</strong> in the sidebar.
    <br><strong>Note:</strong> The <code>default</code> configuration is editable and applies to all repositories not included in another configuration.</li>
  <li>Click <strong>Add new Configuration +</strong>.</li>
  <li>Enter a <strong>Configuration Name</strong> at the top of the page.</li>
</ol>

<h2 id="configuration-walkthrough">Configuration Walkthrough</h2>

<p>The Configurations page shows all your existing repository configurations.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/01-configurations.png" alt="Repository configurations list in DryRun Security dashboard" loading="lazy"></figure>

<p>Click <strong>Add New Configuration</strong> to create a configuration for your repositories.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/02-add-new-config.png" alt="Add New Configuration dialog" loading="lazy"></figure>

<h3 id="select-repositories">Select Repositories</h3>
<p>Choose which repositories this configuration applies to.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/03-select-repos.png" alt="Selecting repositories for a configuration" loading="lazy"></figure>

<h3 id="pr-comments-and-notifications">PR Comments and Notifications</h3>
<p>Enable or disable PR issue comments for this configuration.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/04-issue-comment.png" alt="Issue comment toggle" loading="lazy"></figure>

<p>Enable notifications to get alerts when security findings are detected.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/05-notifications.png" alt="Notifications toggle" loading="lazy"></figure>

<h3 id="attach-policies">Attach Code Policies</h3>
<p>Add up to 7 Custom Code Policies to a configuration.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/06-add-policies.png" alt="Adding code policies to a configuration" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/07-configure-policies.png" alt="Configuring attached policies" loading="lazy"></figure>

<h3 id="configure-security-agents">Code Security Agents</h3>
<p>Configure which security agents are enabled and whether they block or run silently.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/08-configure-agents.png" alt="Configuring code security agents" loading="lazy"></figure>

<p>Save the configuration when complete.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/09-config-save.png" alt="Saving a repository configuration" loading="lazy"></figure>

<h2 id="code-security-agents">Code Security Agents</h2>

<p>The bottom section of the configuration page lists all available Security Analyzers. Each analyzer has its own row with three controls:</p>

<table>
  <thead>
    <tr><th>Analyzer</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Cross-Site Scripting Analyzer</strong></td><td>Detects XSS vulnerabilities across rendering contexts</td></tr>
    <tr><td><strong>General Security Analyzer</strong></td><td>Broad-spectrum analyzer covering auth gaps, crypto, debug artifacts, and more</td></tr>
    <tr><td><strong>IDOR Analyzer</strong></td><td>Surfaces broken object-level authorization</td></tr>
    <tr><td><strong>Mass Assignment</strong></td><td>Detects unsafe model binding patterns</td></tr>
    <tr><td><strong>Secrets Analyzer</strong></td><td>Catches committed credentials, API keys, and tokens</td></tr>
    <tr><td><strong>Server-Side Request Forgery Analyzer</strong></td><td>Identifies SSRF via user-controlled outbound requests</td></tr>
    <tr><td><strong>SQL Injection Analyzer</strong></td><td>Traces data flow to detect unsafe query composition</td></tr>
  </tbody>
</table>

<h2 id="setting-descriptions">Setting Descriptions</h2>

<p>The top section of a configuration provides these controls:</p>

<ul>
  <li><strong>Select Repositories</strong> - A dropdown selector to choose which repositories use this configuration. Repositories can only belong to one configuration at a time; repositories already assigned to another configuration will be greyed out.</li>
  <li><strong>Issue Comment Enabled</strong> - Toggle to enable or disable DryRun Security's PR/MR comment. When enabled, DryRun posts a summary comment on each pull request with findings.</li>
  <li><strong>PR Blocking Enabled</strong> - Toggle to enable PR blocking globally for this configuration. When enabled, findings from configured agents and policies will create GitHub status checks that must pass before merging.</li>
  <li><strong>Notifications Enabled</strong> - Toggle to enable notification delivery. When enabled, choose which integrations receive alerts (see <a href="../docs/slack-integration.html">Notifications</a> for setup details).</li>
  <li><strong>Severity-Based PR Blocking</strong> - Toggle to block PRs based on the vulnerability severity model. When enabled, findings rated Critical or High will prevent the PR from being merged.</li>
  <li><strong>Show Comment for No Findings</strong> - Toggle to control whether DryRun posts a comment even when no security findings are detected. Toggle off for the familiar behavior where DryRun posts a comment only when scans produce findings. Toggle on to have DryRun post a comment on every PR scanned, useful for visibility and audit trails.</li>
  <li><strong>Deduplicate Notifications</strong> - Toggle to reduce duplicate notifications on PRs where the risk level has not changed. When enabled, repeated notifications for the same risk level are suppressed, reducing noise.</li>
</ul>

<h3 id="policy-enforcement">Policy Enforcement Agent</h3>

<p>Below the general settings, the <strong>Policy Enforcement Agent</strong> section lets you attach Custom Code Policies to this configuration:</p>

<ul>
  <li><strong>Add Policy</strong> - Attach an existing policy from your organization's <a href="../docs/custom-code-policies.html">Policy Library</a></li>
  <li><strong>Create Policy</strong> - Write a new Custom Code Policy directly from this screen</li>
</ul>

<p>Each attached policy is shown as a row with its own controls:</p>

<ul>
  <li><strong>Blocking</strong> - Toggle to make this policy a required status check. When enabled, a policy violation prevents the PR from being merged.</li>
  <li><strong>Silent Mode</strong> - Toggle to run the policy without posting findings in the PR comment. Useful for testing new policies before enforcing them.</li>
  <li><strong>Risk Level</strong> - Dropdown to set the severity label returned when the policy has findings. Options are <strong>Risky</strong>, <strong>Fail</strong>, or <strong>Info</strong>.</li>
</ul>

<p>The Policy Enforcement Agent can run up to 7 code policies per repository.</p>
''',
}

PAGES['custom-code-policies'] = {
    'title': 'Custom Code Policies',
    'description': 'Create custom security rules in plain English using Custom Code Policies.',
    'section': 'Platform',
    'content': '''
<h2 id="custom-code-policies">Custom Code Policies</h2>

<p>DryRun Security's Custom Code Policies are a way to define and enforce security policies in a codebase using natural language instead of complex scripting or specialized rule languages.</p>

<p>In this section we demonstrate how to build and save a Custom Code Policy in the DryRun Security Dashboard.</p>


<h2 id="creating-a-policy-walkthrough">Creating a Policy - Visual Walkthrough</h2>

<p>Navigate to the Code Policies section of the DryRun Security dashboard.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/01-code-policies.png" alt="Code Policies list in DryRun Security dashboard" loading="lazy"></figure>

<p>Click <strong>Add New Policy</strong> to start creating a new Custom Code Policy.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/02-add-new.png" alt="Add New Code Policy button" loading="lazy"></figure>

<p>Enter a descriptive name for your policy and fill in the Question, Background, and Guidance fields.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/03-policy-name.png" alt="Naming a new code policy" loading="lazy"></figure>

<p>Select the repository to test the policy against.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/04-policy-repo.png" alt="Selecting a repository for policy testing" loading="lazy"></figure>

<p>Click <strong>Run</strong> to evaluate the policy against a sample PR and review the results.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/05-policy-run.png" alt="Running a code policy for evaluation" loading="lazy"></figure>

<p>Once satisfied with the results, click <strong>Save</strong> to add the policy to your organization.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/nlcp-create/06-policy-save.png" alt="Saving a validated code policy" loading="lazy"></figure>

<h2 id="creating-a-policy">Creating a Policy</h2>

<ol>
  <li>Log in to the DryRun Security portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</li>
  <li>Navigate to the <strong>Code Policies</strong> section. You'll see a list of previously saved Code Policies.</li>
  <li>Click <strong>Add New Code Policy</strong>. You'll see the Code Policy Builder, which can be used to evaluate and save a Custom Code Policy.</li>
  <li>Enter a <strong>Name</strong> for the policy.</li>
  <li>Choose a <strong>Repository</strong> and <strong>Pull Request</strong> to evaluate.</li>
  <li>Enter the Custom Code Policy details:
    <ul>
      <li><strong>Question</strong> (required): A natural language question that identifies whether a specific change relates to the policy. For example, "Does this change expose any sensitive data?"</li>
      <li><strong>Background</strong> (optional): Background information or examples that may be used to refine the evaluation. For example, "We are concerned about..."</li>
      <li><strong>Guidance</strong> (optional): Additional information on actions to take when the policy condition is met.</li>
    </ul>
  </li>
  <li>Click <strong>Run</strong> to see the results of the Code Policy evaluation.</li>
  <li>Once the policy is returning expected results, click <strong>Save</strong> to save it for use in a Repository configuration.</li>
</ol>

<p>To apply the Code Policy to one or more repositories, click <strong>Configure</strong> and follow the steps in <a href="./pr-scanning-configuration.html">Configure Repositories</a>.</p>

<h2 id="policy-enforcement-agent">Policy Enforcement Agent</h2>

<p>When a pull request is opened, DryRun Security's Policy Enforcement Agent runs all configured Custom Code Policies for the repository. The Policy Enforcement Agent can run up to 7 code policies per repository. Results appear in the PR comment and in the GitHub Checks area, with the option to block merges when a policy has findings.</p>

<h2 id="next-steps">Next Steps</h2>

<ul>
  <li>See the <a href="./custom-code-policies.html">Custom Code Policy Starter Pack</a> for ready-to-use policy examples.</li>
  <li>See <a href="./custom-code-policies.html">Custom Code Policy Best Practices</a> for guidance on writing effective policy backgrounds.</li>
  <li>See <a href="./pr-scanning-configuration.html">Configurations</a> to attach policies to repositories.</li>
</ul>


<h2 id="starter-pack">Starter Pack</h2>

<p>The following Custom Code Policies can be used to help you get started. They are generic enough to be customized by your organization but can also be used as-is.</p>

<h2 id="starter-policies">Starter Policies</h2>

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Question</th>
      <th>Background</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>GitHub Action Policy</strong></td>
      <td>Carefully examine any GitHub Actions related changes or inline commands for security risks. Provide results in the form of a list with line numbers and with the title: Identified GitHub Actions Risks.</td>
      <td>Concerned about: use of untrusted or mutable third-party actions; secrets exposure; unsafe use of <code>run:</code> commands; privilege escalation; insecure usage of <code>pull_request_target</code> trigger; workflow that can be triggered by forks with write access to secrets.</td>
    </tr>
    <tr>
      <td><strong>New API Endpoint w/o authz</strong></td>
      <td>Does this code introduce a new API endpoint without authorization enforcement?</td>
      <td>Concerned about new API routes or endpoints being added without any type of enforcement. Check default framework annotations or a specified access definitions file to determine if the endpoint has been added without authz.</td>
    </tr>
    <tr>
      <td><strong>Third Party Scripts</strong></td>
      <td>Does any file in the codebase include references (e.g., via <code>&lt;script&gt;</code> tags, import/require statements, or dynamic loading functions) to third-party scripts?</td>
      <td>Introducing third-party scripts means trusting an external source to provide code that will run in user browsers. If a CDN or third-party host is compromised, users could be exposed to malicious behavior (e.g., credential theft, data exfiltration, crypto mining).</td>
    </tr>
    <tr>
      <td><strong>Logging Sensitive Data</strong></td>
      <td>Does any logging function in the codebase output sensitive data (such as passwords, API keys, or session tokens)?</td>
      <td>Logging sensitive data can inadvertently expose secrets if logs are accessed by unauthorized parties.</td>
    </tr>
    <tr>
      <td><strong>Username Enumeration</strong></td>
      <td>Does this change introduce username enumeration flaws?</td>
      <td>Username enumeration flaws typically happen when system error messages indicate the presence of a user in a system and can be used by malicious actors to find valid usernames.</td>
    </tr>
    <tr>
      <td><strong>Token Validation Check</strong></td>
      <td>Are there any logical flaws in our token validation or generation logic?</td>
      <td>Tokens need to be generated using a secure algorithm that has high entropy, and they must be validated before use.</td>
    </tr>
    <tr>
      <td><strong>Insecure File Upload Handling</strong></td>
      <td>Does this change introduce or modify file upload functionality in a way that might allow dangerous file types or bypass security controls?</td>
      <td>File uploads, if not strictly validated, pose a risk of allowing attackers to send files that could be executed server-side (e.g., web shells) or cause other harm.</td>
    </tr>
    <tr>
      <td><strong>Improper Error Handling</strong></td>
      <td>Does this change expose detailed internal error messages or stack traces to end users that might reveal sensitive application internals?</td>
      <td>Detailed error messages or stack traces can provide attackers with insights into the application structure, technology stack, or logic.</td>
    </tr>
    <tr>
      <td><strong>Insufficient CORS Configuration</strong></td>
      <td>Does this change modify Cross-Origin Resource Sharing (CORS) settings in a way that might allow unauthorized cross-origin access?</td>
      <td>Overly permissive CORS settings can open the door to cross-origin attacks or unintended data leakage.</td>
    </tr>
    <tr>
      <td><strong>Insecure Inter-Service Communication</strong></td>
      <td>Does this change affect how microservices communicate, potentially bypassing secure channels, authentication, or authorization between services?</td>
      <td>In a microservices architecture, inter-service communication often transmits sensitive data. If communication is not secured, attackers may intercept or manipulate data.</td>
    </tr>
    <tr>
      <td><strong>Insecure Deserialization Handling</strong></td>
      <td>Does this change deserialize data from untrusted sources without proper validation or secure safeguards?</td>
      <td>Unvalidated deserialization of data can lead to severe vulnerabilities, including remote code execution (RCE) or privilege escalation.</td>
    </tr>
    <tr>
      <td><strong>PHI/PII Exposure</strong></td>
      <td>Does this change result in the exposure of sensitive PII or PHI through code, logs, network transmissions, or repository artifacts?</td>
      <td>Exposing PII/PHI can lead to severe privacy breaches, legal ramifications, and reputational damage. Must comply with HIPAA, GDPR, or other applicable standards.</td>
    </tr>
    <tr>
      <td><strong>Hard-Coded Credentials Detection</strong></td>
      <td>Does this change introduce hard-coded credentials such as passwords, API keys, tokens, or secret access keys?</td>
      <td>Hard-coding credentials directly into source code poses a serious security risk. Include file path and line number in results. Do not repeat the credentials in the results.</td>
    </tr>
  </tbody>
</table>
</div>


<h2 id="best-practices">Best Practices</h2>

<p>When you provide more clarity in your Custom Code Policy's background, your policy becomes more reliable and accurate. The tips below help your policies accurately scope which files are considered, reason about your code, and decide when deeper analysis is necessary.</p>

<h2 id="what-is-a-background">What Is a Background?</h2>

<p>When writing your Custom Code Policy, you provide:</p>
<ul>
  <li><strong>Question:</strong> The question to ask against a pull request. This should be a yes or no question.</li>
  <li><strong>Background:</strong> Optional background information about the question. This provides context for your question.</li>
  <li><strong>Guidance:</strong> Optional guidance your policy will provide to a viewer when a finding is identified. This should be a clear set of instructions.</li>
</ul>

<h2 id="scope-file-paths">1. Scope File Paths When Possible</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Only apply this check to files in <code>/src/controllers/**</code>"</li>
  <li>"Limit this check to files under <code>services/auth/</code> and <code>middleware/</code>"</li>
</ul>

<p><strong>Avoid this:</strong></p>
<ul>
  <li>"Check the whole codebase for this" - too vague, slow, and may introduce noise</li>
  <li>"Anywhere this might happen" - ambiguous and not helpful for targeting</li>
</ul>

<h2 id="target-specific-layers">2. Target Specific Layers or Components</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Authorization is enforced at the controller layer - be sure to check it"</li>
  <li>"Verify any additions to the service layer that might bypass our middleware"</li>
</ul>

<p><strong>Avoid this:</strong></p>
<ul>
  <li>"Just make sure this is secure" - doesn't guide where your policy should look or what to expect</li>
  <li>"Check backend stuff" - too generic</li>
</ul>

<h2 id="use-naming-cues">3. Use File or Function Naming Cues</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Look for function names starting with <code>validate</code> or containing <code>auth</code>"</li>
  <li>"Check for uses of <code>unsafeEval()</code> or similar patterns in JavaScript"</li>
</ul>

<h2 id="indicate-pr-diffs">4. Indicate When Only PR Diffs Should Be Analyzed</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Only analyze changes introduced in this PR"</li>
  <li>"Ignore unchanged files - only evaluate lines added or modified"</li>
</ul>

<h2 id="mention-full-file-analysis">5. Mention When Full-File or Tool-Based Analysis Is Needed</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"If a helper is called, trace its definition from the imports"</li>
  <li>"Use search tools if the current file doesn't define the authorization logic"</li>
</ul>

<h2 id="explain-indirection">6. Explain Known Indirection Patterns</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Database access may happen via helper functions in <code>db/helpers.ts</code>"</li>
  <li>"Authorization is often wrapped in <code>ensureAuthorizedUser()</code> - follow that chain"</li>
</ul>

<h2 id="define-secure">7. Define What "Secure" Means</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Tokens must be validated using <code>secureCompare()</code>"</li>
  <li>"CORS must not allow <code>*</code> unless <code>isTrustedOrigin(origin)</code> returns <code>true</code>"</li>
</ul>

<p><strong>Avoid this:</strong></p>
<ul>
  <li>"Just make sure it is secure" - every organization defines "secure" differently</li>
  <li>"CORS should be safe" - what does "safe" mean?</li>
</ul>

<h2 id="call-out-enforcement-mechanisms">8. Call Out Recognized Enforcement Mechanisms</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Authorization is enforced via the <code>require_role</code> decorator"</li>
  <li>"Secure file uploads must go through <code>validateFileType()</code>"</li>
</ul>

<h2 id="avoid-vague-language">9. Avoid Vague or Abstract Language</h2>

<p><strong>Do this:</strong></p>
<ul>
  <li>"Check that logging statements do not include variables like <code>password</code>, <code>token</code>, or <code>apiKey</code>"</li>
</ul>

<p><strong>Avoid this:</strong></p>
<ul>
  <li>"Make sure secrets are not logged" - what is a "secret"? What logging system?</li>
  <li>"Scan for unsafe logging" - what qualifies as unsafe?</li>
</ul>


<h2 id="policy-library">Policy Library</h2>

<h2 id="overview">Overview</h2>

<p>The Policy Library provides curated, pre-built <a href="../docs/custom-code-policies.html">Custom Code Policy</a> templates that you can deploy immediately or customize for your organization. Instead of writing policies from scratch, start from a tested template and adapt it to your specific architecture and requirements.</p>

<h2 id="policy-categories">Policy Categories</h2>

<h3 id="owasp-top-10">OWASP Top 10</h3>
<p>Policies targeting the most common web application vulnerability classes:</p>
<ul>
  <li>"Does this change introduce SQL injection by constructing queries from user input?"</li>
  <li>"Does this code render user input in HTML without proper escaping?"</li>
  <li>"Does this change introduce an API endpoint that accesses resources without verifying the requesting user owns them?"</li>
</ul>

<h3 id="auth-patterns">Authentication and Authorization</h3>
<p>Policies for access control enforcement:</p>
<ul>
  <li>"Does this change introduce a new API endpoint without authorization enforcement?"</li>
  <li>"Does this change introduce username enumeration through different error messages for valid and invalid usernames?"</li>
  <li>"Does this code store or transmit passwords in plaintext?"</li>
</ul>

<h3 id="secrets-handling">Secrets Handling</h3>
<p>Policies for credential management:</p>
<ul>
  <li>"Does this change commit API keys, tokens, or passwords that should be stored in environment variables?"</li>
  <li>"Does this code log sensitive data like passwords, tokens, or personal information?"</li>
</ul>

<h3 id="ai-code-guidelines">AI-Generated Code Guidelines</h3>
<p>Policies for teams using AI coding assistants:</p>
<ul>
  <li>"Does this AI-generated code include hardcoded credentials that should be environment variables?"</li>
  <li>"Does this change introduce a dependency not in our approved list?"</li>
</ul>

<h3 id="compliance-policies">Compliance</h3>
<p>Policies for regulatory requirements:</p>
<ul>
  <li>"Do any libraries introduced in this PR violate our internal licensing requirements?"</li>
  <li>"Does this change handle personal data without proper consent or encryption?"</li>
</ul>

<h2 id="using-library-policies">Using Library Policies</h2>

<ol>
  <li><strong>Browse the library</strong> in the DryRun Security platform to find policies that match your needs</li>
  <li><strong>Preview and customize</strong> - adjust the policy language to match your specific architecture, frameworks, and terminology</li>
  <li><strong>Test before deploying</strong> - use the AI Policy Assistant to run the policy against recent PRs and verify it produces the expected results</li>
  <li><strong>Deploy</strong> - enable the policy for selected repositories or your entire organization</li>
</ol>

<h2 id="ai-policy-assistant">AI Policy Assistant</h2>

<p>The AI Policy Assistant helps you draft, refine, and test policies through a guided workflow:</p>

<ul>
  <li><strong>Describe your goal</strong> in natural language - "I want to prevent debug endpoints from reaching production"</li>
  <li><strong>Refine the policy</strong> - the assistant suggests specific language that accounts for your frameworks and patterns</li>
  <li><strong>Test against recent PRs</strong> - see what the policy would have flagged on real code changes before enabling it</li>
  <li><strong>Iterate</strong> - adjust the wording and re-test until the policy catches what you want without false positives</li>
</ul>

<h2 id="related-pages">Related Pages</h2>

<ul>
  <li><a href="../docs/custom-code-policies.html">Custom Code Policies</a> - how Custom Code Policy works</li>
  <li><a href="../docs/custom-code-policies.html">Custom Code Policy Starter Pack</a> - getting started with your first policies</li>
  <li><a href="../docs/custom-code-policies.html">Custom Code Policy Best Practices</a> - writing effective policies</li>
</ul>
''',
}

PAGES['repository-context'] = {
    'title': 'Repository Context',
    'description': 'Provide repository context with AGENTS.md to improve DryRun Security analysis accuracy.',
    'section': 'Platform',
    'content': '''
<p><a href="https://agents.md/" target="_blank" rel="noopener noreferrer">AGENTS.md</a> is a format supported by the <a href="https://aaif.io/" target="_blank" rel="noopener noreferrer">Agentic AI Foundation</a>, a Linux Foundation Project. The file is intended to be "a predictable place to provide the context and instructions to help AI coding agents work on your project."</p>

<p>DryRun Security supports <code>AGENTS.md</code> for both core analyzer products: the Code Review Agent and the DeepScan Agent. DryRun Security's agents will look for and review this file to apply the additional context it provides during analysis.</p>

<p><strong>Note:</strong> The Code Review Agent checks for AGENTS.md in the root. The DeepScan Agent can discover both root and nested AGENTS.md files.</p>

<h2 id="what-to-include">What to Include</h2>

<p>You can use <code>AGENTS.md</code> to describe your application structure, test and build instructions for coding agents, integration definitions, and more. That same information can also provide valuable context to DryRun Security's agents.</p>

<p>To best leverage this feature, add a <strong>Security Review Guidelines</strong> section to your <code>AGENTS.md</code> with any additional context related to design assumptions, areas of particular security interest, or other relevant points helpful for an agentic security reviewer.</p>

<p>Context ideas for Security Agents:</p>
<ul>
  <li>Structure of a monolith, and how authorization works between components</li>
  <li>Collections of routes or controllers that do not follow typical authorization patterns by design</li>
  <li>Specific security requirements coding assistants need to validate against during code generation</li>
  <li>Assumptions about security-impacting configurations not clear in code (e.g., TLS offloading, WAF rules)</li>
  <li>Specific security patterns that must be followed, with examples of allowed and disallowed code snippets</li>
</ul>

<h2 id="example">Example Security Review Guidelines Section</h2>

<pre><code>## Security Review Guidelines

### Device Trust for internal routes
All routes that are prefixed with /abc123 are to be recognized
as internal-only routes, and require the use of trusted devices
issued by the enterprise. Device trust is recognized by an Okta
device token, and these routes are verified within Okta for
proper authorization scopes from the IdP and authorization
server, which will not be checked by the application layer
specifically. Row or object-level authorization issues related to
this pattern only for these internal routes can be ignored as
accepted.

### Intentionally Public Routes
Some controllers have embedded routes with authentication and
authorization decorators disabled or skipped on purpose for
public facing content. The routes are intended to allow anonymous
access to these features ONLY IF the specific controller action
does not perform edits or require write access. Validate the read-
only nature of these endpoints and flag any actions that enable
write behavior when the authentication decorations are skipped.

### Ignore HTTPS related issues on cookies and configuration files
This application is always deployed to a kubernetes cluster as a
mesh service. TLS offloading is provided in front of the application.
Ignore any issues related to Cookies missing Secure flags, requiring
HTTPS in build configurations, or certificate requirements in
this application.</code></pre>

''',
}

PAGES['risk-register'] = {
    'title': 'Risk Register',
    'description': 'One view to see, search, and act on all security risk across your organization.',
    'section': 'Platform',
    'content': '''
<p>The Risk Register is the working space for AppSec engineers, designed to surface findings that need action taken. It aggregates findings from two sources: the <a href="./pr-scanning.html">PR Scanner</a>, which reviews every pull request for vulnerabilities in real time, and <a href="./deepscan.html">DeepScan</a>, which performs full-repository security analysis on demand. Findings range from critical vulnerabilities and secrets exposures to policy violations and dependency risks. Because these findings represent real or potential security issues in your codebase, the Risk Register provides a single place to review, triage, and act on them before they become incidents.</p>

<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/risk-register/01-risk-register.png" alt="DryRun Security Risk Register dashboard" loading="lazy"></figure>

<h2 id="severity-overview">Severity Overview</h2>

<p>At the top of the Risk Register, four severity cards display the current count of findings by level:</p>

<ul>
  <li><strong>Critical</strong> - Findings that represent immediate, exploitable risk</li>
  <li><strong>High</strong> - Significant vulnerabilities that should be prioritized</li>
  <li><strong>Medium</strong> - Moderate-risk issues to address during normal development</li>
  <li><strong>Low</strong> - Informational findings or minor concerns</li>
</ul>

<p>These cards provide an at-a-glance view of your organization's current risk distribution, making it easy to see where attention is needed most.</p>

<h2 id="search-and-filter">Search and Filter</h2>

<p>Below the severity cards, the Risk Register provides several ways to narrow your view:</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/risk-register/02-risk-filter.png" alt="Risk Register filtering and search options" loading="lazy"></figure>

<ul>
  <li><strong>Search</strong> - A full-text search box lets you search across finding titles, file paths, repository names, PR titles, PR numbers, and other fields</li>
  <li><strong>30D date filter</strong> - Quickly scope findings to the last 30 days, or adjust the date range to match your review period</li>
  <li><strong>Filter</strong> - Opens advanced filtering options to narrow by risk level, agent type (including Code Policy), status, and more</li>
  <li><strong>Triage</strong> - Select one or more findings and triage them in bulk with a reason and optional context</li>
</ul>

<h2 id="findings-table">Findings Table</h2>

<p>The main findings table shows all findings with the following columns:</p>

<table>
  <thead>
    <tr><th>Column</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Risk</strong></td><td>Severity label (Critical, High, Medium, Low) with color coding. Sortable.</td></tr>
    <tr><td><strong>Type</strong></td><td>The vulnerability or finding description (e.g., "Authorization Bypass in Next.js", "Token Validation Check", "client-side-trust")</td></tr>
    <tr><td><strong>File</strong></td><td>The file path where the finding was detected (e.g., <code>package-lock.json</code>, <code>app/api/generate-vi...</code>, <code>firestore.rules</code>)</td></tr>
    <tr><td><strong>Repo</strong></td><td>The repository name where the finding originated</td></tr>
    <tr><td><strong>Detected</strong></td><td>Timestamp showing when the finding was first detected (e.g., 03/18/26 16:51:18)</td></tr>
    <tr><td><strong>Agent</strong></td><td>Which agent produced the finding - SCA, Code Policy, DeepScan, or a specific Security Analyzer</td></tr>
    <tr><td><strong>Status</strong></td><td>The current state of the finding, shown as an icon indicating open, triaged, or resolved</td></tr>
  </tbody>
</table>

<p>Each row has a checkbox for bulk selection, and findings are paginated (e.g., "Showing 1-20 of 203 entries") with page navigation at the bottom.</p>

<h2 id="finding-triage">Finding Triage</h2>

<p>Risk Register supports Finding Triage so teams can categorize findings and feed decisions back into DryRun Security. Every triage decision - the reason, the context you provide - is a learning signal that improves future scan accuracy. See <a href="../finding-tuning.html">Finding Triage</a> for the full workflow.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/risk-register/03-finding-triage.png" alt="Finding triage in the Risk Register" loading="lazy"></figure>

<p>Select one or more findings using the checkboxes, then click <strong>Triage</strong> to choose a reason and optionally add context. When you mark a finding as <strong>False Positive</strong>, DryRun Security fingerprints the vulnerability pattern and suppresses it in future scans automatically. The context you provide feeds into the Knowledge Graph to improve detection accuracy over time.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/risk-register/04-triage-pr.png" alt="Finding triage from the PR workflow" loading="lazy"></figure>

<h2 id="dismissed-findings">Dismissed Findings</h2>

<p>You can view and manage dismissed findings in the Risk Register using the <strong>Dismissed</strong> filter option. This shows all previously dismissed findings with full context: the dismissal category, reason, who dismissed it, when, and any notes provided at the time of dismissal.</p>

<p>Each dismissed finding has a <strong>Restore</strong> button to bring it back to your active queue if circumstances change or the dismissal needs to be revisited.</p>

<p>The dismissal flow includes <strong>Resolved</strong> and <strong>Won&rsquo;t Fix / Nitpick</strong> values in addition to the standard options, giving teams more precise categorization when triaging findings.</p>

<h2 id="faqs">FAQs</h2>

<p><strong>How are severities determined?</strong><br>
DryRun Security normalizes outputs to Critical, High, Medium, and Low. For PR scans, these align with Fail, Risky, and Info labels from the analyzers. DeepScan uses its own severity model and outputs are normalized similarly.</p>

<p><strong>Which columns can I sort?</strong><br>
Risk is the primary sortable column. Type, File, Repo, Detected, Agent, and Status columns are also sortable.</p>

<p><strong>What agents appear in the Agent column?</strong><br>
You will see SCA (Software Composition Analysis), Code Policy (Custom Code Policies), DeepScan, and individual <a href="../docs/pr-variant-analysis.html">Security Analyzers</a> listed as the source of each finding.</p>

<h2 id="common-workflows">Common Workflows</h2>

<h3 id="reviewing-merged-risk">Reviewing Merged Risk</h3>
<p>Filter by &ldquo;merged&rdquo; PR status. This shows findings DryRun Security identified as containing a vulnerability but that were merged anyway &mdash; the vulnerability lives in the codebase. These represent accepted or overlooked risk and should be reviewed to determine if remediation is needed.</p>

<h3 id="triaging-open-prs">Triaging Open PRs</h3>
<p>Filter by &ldquo;open&rdquo; PR status. This surfaces findings on pull requests that are still open and have not been merged to main yet. Because the PR is still open, there is still time to fix the issue before it reaches production &mdash; these findings should be prioritized and actioned first.</p>

<h3 id="reviewing-dismissed-findings">Reviewing Dismissed Findings</h3>
<p>Filter to show dismissed findings. AppSec engineers can see who dismissed each finding and take appropriate follow-up action: override the dismissal if the finding represents real risk, reach out to the developer to help educate them, or stay informed about what is being marked as &ldquo;won&rsquo;t fix&rdquo;, &ldquo;nit pick&rdquo;, or &ldquo;false positive&rdquo;. This workflow supports both risk oversight and developer security education.</p>
''',
}

PAGES['finding-tuning'] = {
    'title': 'Finding Tuning with Feedback',
    'description': 'Tune security findings and reduce false positives with feedback.',
    'section': 'Platform',
    'content': '''
<h2 id="finding-triage">Finding Triage</h2>

<p>Every triage decision makes DryRun Security smarter. When you triage a finding - whether you mark it as a false positive, accept the risk, or add context - DryRun Security learns from that decision and applies it to future scans across your organization.</p>

<h2 id="how-dryrun-learns">How DryRun Security Learns from Triage</h2>

<p>Most security tools treat triage as a dead end: you dismiss a finding, and it disappears until it shows up again next week. DryRun Security treats every triage decision as a learning signal:</p>
<ul>
  <li><strong>False positive fingerprinting</strong> - When you mark a finding as a false positive, DryRun Security fingerprints the vulnerability pattern and automatically suppresses it in future PR scans and DeepScans.</li>
  <li><strong>Context-based learning</strong> - When you add context explaining why a finding is safe, that context is stored and used to calibrate future analysis in similar situations across your codebase.</li>
  <li><strong>Pattern recognition</strong> - Over time, triage decisions feed into the <a href="../docs/architecture-risks.html">Code Security Knowledge Graph</a>, improving accuracy for your specific frameworks, deployment patterns, and risk profile.</li>
</ul>
<p>The result: false positive rates decrease over time as DryRun Security accumulates organizational knowledge from your team's triage decisions.</p>

<h2 id="triaging-a-finding">Triaging a Finding</h2>

<p>In the Risk Register, click <strong>Triage</strong> on a finding to:</p>
<ul>
  <li>Select a triage reason (for example: False Positive, Accepted Risk, Won't Fix)</li>
  <li>Add supporting context in a text box explaining your reasoning</li>
</ul>
<p>The more context you provide, the more DryRun Security can learn from the decision. Even a short explanation helps improve future scan accuracy.</p>

<h2 id="false-positive-fingerprinting">False Positive Fingerprinting</h2>

<p>When you mark a finding as <strong>False Positive</strong>:</p>
<ul>
  <li>DryRun Security creates a fingerprint of that vulnerability pattern.</li>
  <li>Future PR scans and DeepScans automatically suppress the finding when the same fingerprint is detected, so it does not come back.</li>
  <li>The fingerprint and your context are stored in the Knowledge Graph and used to improve detection accuracy for similar patterns.</li>
</ul>

<h2 id="context-based-learning">Context-Based Learning</h2>

<p>When you include context in the triage text box, DryRun Security uses it in two ways:</p>
<ul>
  <li><strong>Immediate suppression</strong> - Similar false positives matching the context are suppressed in future scans.</li>
  <li><strong>Long-term learning</strong> - The context feeds into the Knowledge Graph to improve analysis for similar code patterns, framework behaviors, and deployment topologies.</li>
</ul>

<p>Examples of useful context:</p>
<ul>
  <li>"This endpoint is only accessible from internal services - no user input reaches this code path."</li>
  <li>"TLS offloading is handled upstream; the application does not need to enforce HTTPS internally."</li>
  <li>"This query is constructed only from validated constants, never from user input."</li>
</ul>

<h2 id="triage-from-pr-workflow">Triage from the PR Workflow</h2>

<p>Developers can also triage findings directly from GitHub and GitLab comments - marking findings as false positives and adding context without leaving the PR workflow. Those triage decisions flow into the Risk Register and feed the same learning loop, keeping the feedback close to where developers work.</p>

<h2 id="faqs">FAQs</h2>

<p><strong>What is Finding Triage?</strong><br>
Finding Triage lets you categorize a finding and record why, using a triage reason and optional context. Triaged findings are marked resolved in the UI, and the decisions feed back into DryRun Security to improve future scans.</p>

<p><strong>Does DryRun Security actually learn from my triage decisions?</strong><br>
Yes. Every triage decision - the reason, the context you provide, the fingerprint - is stored in the Code Security Knowledge Graph. DryRun Security uses this to suppress duplicate findings immediately and to improve detection accuracy for similar patterns over time.</p>

<p><strong>What happens when I mark a finding as a False Positive?</strong><br>
DryRun Security fingerprints the vulnerability pattern. If the same fingerprint is detected in a future PR scan or DeepScan, the finding is automatically suppressed.</p>

<p><strong>How is the context field used?</strong><br>
Context is stored with the triage decision and used in two ways: immediately to suppress similar false positives, and over time to improve analysis accuracy through the Knowledge Graph.</p>

<p><strong>Can developers triage findings from their PR workflow?</strong><br>
Yes. Developers can triage findings directly from GitHub and GitLab comments. Those decisions sync to the Risk Register and feed the same learning loop.</p>


<h2 id="false-positive-reduction">False Positive Reduction</h2>

<h2 id="the-false-positive-problem">The False Positive Problem</h2>

<p>False positives are the defining problem of traditional static analysis. When a tool flags code that is not actually vulnerable, developers lose time investigating, lose trust in the tool, and eventually start ignoring findings entirely. Studies consistently show that legacy SAST tools produce false positive rates of 40-60% or higher, meaning more than half of all alerts are noise.</p>

<p>The consequence is predictable: development teams either disable the tool, suppress entire categories of findings, or assign a dedicated person to triage alerts - none of which improve security.</p>

<h2 id="why-pattern-matching-fails">Why Pattern Matching Produces Noise</h2>

<p>Pattern-matching tools flag code based on syntactic similarity to known vulnerability patterns. A function call that looks like a SQL query with string concatenation gets flagged, regardless of whether:</p>

<ul>
  <li>The input is actually user-controlled</li>
  <li>The input has already been sanitized upstream</li>
  <li>The code is behind an authorization check that limits access</li>
  <li>The string being concatenated is a constant, not a variable</li>
  <li>The framework being used has built-in protections</li>
</ul>

<p>Every one of these cases produces a false positive in a pattern-matching tool. The tool sees the pattern but cannot evaluate whether the pattern represents real risk in context.</p>

<h2 id="contextual-analysis-approach">The Contextual Analysis Approach</h2>

<p>DryRun Security's <a href="../docs/security-reviews.html">Contextual Security Analysis</a> engine evaluates each potential finding against the surrounding code context before reporting it. This means the engine considers:</p>

<ul>
  <li><strong>Data flow</strong> - tracing where input originates and whether it passes through sanitization before reaching a sensitive sink</li>
  <li><strong>Authorization context</strong> - whether the code path is protected by authentication and authorization middleware</li>
  <li><strong>Framework behavior</strong> - understanding that Django's ORM parameterizes queries by default, that React escapes JSX output, that Spring Security's CSRF protection is enabled by default</li>
  <li><strong>Developer intent</strong> - recognizing test fixtures, example configurations, and development-only code paths</li>
  <li><strong>Exploitability</strong> - assessing whether a theoretical vulnerability is actually reachable and exploitable in the deployed application</li>
</ul>

<p>The result is findings that represent genuine risk, not syntactic matches.</p>

<h2 id="90-lower-noise">90% Lower Noise in Practice</h2>

<p>DryRun Security's contextual approach produces approximately 90% fewer false positives compared to traditional pattern-matching SAST tools. This is not achieved through suppression or threshold tuning - it is the natural result of analyzing code in context rather than in isolation.</p>

<p>In practical terms, a traditional tool that generates 100 findings on a codebase might have 50-60 false positives that require manual review. DryRun Security analyzing the same codebase would produce fewer total findings, with the overwhelming majority representing actionable, real vulnerabilities.</p>

<h2 id="not-suppression">Reduction, Not Suppression</h2>

<p>It is important to distinguish between false positive <strong>reduction</strong> and false positive <strong>suppression</strong>. Many tools achieve lower noise by letting users suppress finding categories, raise severity thresholds, or ignore entire file paths. This hides findings but does not prevent them from being generated.</p>

<p>DryRun Security reduces false positives at the analysis stage. The <a href="../docs/pr-variant-analysis.html">specialized analyzers</a> evaluate context before generating a finding, so noise is eliminated before it reaches the developer. Suppression workflows exist for the rare false positive that does occur (see <a href="../docs/finding-tuning.html">Finding Triage</a>), but they are the exception rather than the primary noise management strategy. Every triage decision feeds back into DryRun Security to improve future accuracy.</p>

<h2 id="developer-trust">Impact on Developer Trust</h2>

<p>When developers trust that findings represent real issues, they act on them. Low false positive rates create a positive feedback loop: developers investigate findings promptly, fix real vulnerabilities, and continue to engage with the tool rather than working around it.</p>

<p>This is why DryRun Security's approach to false positive reduction is not just a technical feature - it is the foundation of a security workflow that developers actually adopt.</p>
''',
}

PAGES['pr-blocking'] = {
    'title': 'PR Blocking',
    'description': 'Configure DryRun Security to block pull requests when critical vulnerabilities are detected.',
    'section': 'Platform',
    'content': '''
<h2 id="overview">Overview</h2>

<p>DryRun Security can be configured to block pull requests from being merged when security findings exceed your defined thresholds. PR Blocking integrates with your source code management platform's native branch protection features to enforce security gates in your development workflow.</p>

<h2 id="how-it-works">How It Works</h2>

<p>When PR Blocking is enabled, DryRun Security reports its scan results as a required status check on each pull request. If findings meet or exceed the configured severity threshold, the check is marked as failed, preventing the PR from being merged until the issues are resolved.</p>

<ul>
  <li><strong>GitHub:</strong> DryRun Security integrates with GitHub's required status checks. Configure the DryRun Security check as required in your branch protection rules.</li>
  <li><strong>GitLab:</strong> DryRun Security integrates with GitLab's merge request approval rules to block merges when findings are present.</li>
</ul>

<h2 id="configuring-blocking">Configuring PR Blocking</h2>

<ol>
  <li>Navigate to the <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">DryRun Security dashboard</a>.</li>
  <li>Go to <strong>Settings</strong> for the repository you want to configure.</li>
  <li>Under <strong>PR Blocking</strong>, enable the blocking toggle.</li>
  <li>Set the <strong>severity threshold</strong> - findings at or above this level will block the PR. Options include:
    <ul>
      <li><strong>Critical</strong> - Only block on critical severity findings.</li>
      <li><strong>High</strong> - Block on high and critical findings.</li>
      <li><strong>Medium</strong> - Block on medium, high, and critical findings.</li>
      <li><strong>Low</strong> - Block on all findings.</li>
    </ul>
  </li>
  <li>Configure your SCM's branch protection to require the DryRun Security status check.</li>
</ol>

<h2 id="override-workflow">Override Workflow</h2>

<p>In cases where a blocked PR needs to be merged despite findings (for example, an accepted risk or false positive), authorized users can override the block:</p>

<ul>
  <li>Use <a href="./finding-tuning.html">Finding Tuning with Feedback</a> to mark findings as accepted risk or false positive.</li>
  <li>Repository administrators can bypass branch protection rules when necessary.</li>
  <li>All overrides are logged in the <a href="./risk-register.html">Risk Register</a> for audit purposes.</li>
</ul>

<h2 id="configure-blocking">Configure Blocking with Branch Protection</h2>

<p>Both Custom Code Policies and Code Security Agents can be used with GitHub Branch Protection Rules to block PRs from being merged. After enabling <strong>Blocking</strong> on a policy or analyzer, follow these steps:</p>

<h3 id="set-up-branch-protection">Set Up a Classic Branch Protection Rule</h3>

<ol>
  <li>On GitHub, navigate to the main page of the repository.</li>
  <li>Under your repository name, click <strong>Settings</strong>.</li>
  <li>In the <strong>Code and automation</strong> section of the sidebar, click <strong>Branches</strong>.</li>
  <li>Choose <strong>Add classic branch protection rule</strong>.</li>
  <li>Under <strong>Branch name pattern</strong>, type the name of the branch to protect (e.g., <code>main</code>).</li>
  <li>Select <strong>Require status checks to pass before merging</strong>.</li>
  <li>In the search field, search for DryRun Security status checks to require. Choose <strong>Code Policies</strong> for Custom Code Policies, or the agent name (e.g., <strong>Secrets Analyzer</strong>) for Code Security Agents.</li>
  <li>Click <strong>Create</strong>.</li>
</ol>

<p>When a Custom Code Policy has <strong>Blocking</strong> enabled, it appears as a single Check in GitHub under the name <strong>Code Policies</strong>. When a Code Security Agent has blocking enabled, it appears as a Check with the agent's name (e.g., <strong>Secrets Analyzer</strong>).</p>

<h2 id="github-branch-protection-rules">GitHub Branch Protection Rules</h2>

<p>Use GitHub Branch Protection Rules to enforce DryRun Security checks before merging.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/10-github-settings.png" alt="GitHub repository Settings page" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/11-github-branches.png" alt="GitHub Branches settings" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/12-branch-protection.png" alt="GitHub Branch Protection rule" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/13-branch-name.png" alt="Branch name pattern for protection" loading="lazy"></figure>

<p>Require DryRun Security status checks to pass before merging.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/14-require-checks.png" alt="Requiring status checks for DryRun Security" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/15-checks-policies.png" alt="DryRun Security policy checks in branch protection" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/16-checks-secrets.png" alt="DryRun Security secrets check in branch protection" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/configurations/17-checks-details.png" alt="DryRun Security check details in branch protection" loading="lazy"></figure>
''',
}

PAGES['compliance-grc'] = {
    'title': 'Compliance & GRC',
    'description': 'Compliance reporting, audit readiness, and SBOM generation.',
    'section': 'Platform',
    'content': '''
<h2 id="compliance-audit">Compliance and Audit Readiness</h2>

<h2 id="overview">Overview</h2>

<p>DryRun Security provides the evidence trail that compliance and audit workflows require. Every PR review, finding, remediation, and policy enforcement action is tracked and accessible through the platform's reporting capabilities.</p>

<h2 id="soc2-certification">SOC2 Type II Certification</h2>

<p>DryRun Security is SOC2 Type II certified. This means the platform itself has been independently audited for security, availability, and confidentiality controls. Your data is handled according to the same standards your organization is working to meet.</p>

<h2 id="audit-evidence">Audit Evidence Generation</h2>

<p>The platform automatically generates evidence that auditors and regulators commonly request:</p>

<ul>
  <li><strong>Findings history</strong> - complete record of every vulnerability found, when it was found, and when it was resolved</li>
  <li><strong>Remediation timelines</strong> - time-to-fix metrics for each finding, broken down by severity and category</li>
  <li><strong>Policy enforcement records</strong> - which <a href="../docs/custom-code-policies.html">Custom Code Policies</a> were evaluated, what they found, and how findings were resolved</li>
  <li><strong>Scan coverage</strong> - which repositories were scanned, how frequently, and what percentage of PRs received security review</li>
  <li><strong>DeepScan reports</strong> - point-in-time full-repository security assessments for baseline evidence</li>
</ul>

<h2 id="dashboard-reporting">Dashboard and Reporting</h2>

<p>The <a href="../docs/application-summary.html">Security Dashboard</a> provides real-time metrics that map to common compliance requirements:</p>

<ul>
  <li>Vulnerability trends over time (are things getting better or worse?)</li>
  <li>Open findings by severity and category</li>
  <li>Mean time to remediation</li>
  <li>Policy compliance rates across repositories</li>
  <li>Coverage gaps (repositories not yet connected)</li>
</ul>

<p>Use the <a href="../docs/feature-ships.html">intelligence index</a> to generate custom audit-ready reports by asking natural language questions like "show me a chart of risky alerts by repo for last quarter."</p>

<h2 id="risk-register">Risk Register as Audit Trail</h2>

<p>The <a href="../docs/risk-register.html">Risk Register</a> serves as the central audit trail for all findings. Every finding includes:</p>

<ul>
  <li>The specific code change that introduced the vulnerability</li>
  <li>Which analyzer detected it and why</li>
  <li>The remediation status and any associated PR that fixed it</li>
  <li>Triage records with notes explaining why a finding was marked as acceptable risk</li>
</ul>

<p>This level of traceability satisfies auditors who need to understand not just what vulnerabilities exist, but how the organization identified and responded to them.</p>

<h2 id="sbom-and-ai-bom">SBOM and AI-BOM</h2>

<p>DryRun Security generates <a href="../docs/compliance-grc.html">Software Bills of Materials (SBOM)</a> that document the third-party components in your codebase. SBOMs are increasingly required by regulation (Executive Order 14028, EU Cyber Resilience Act) and by enterprise customers who need supply chain transparency.</p>

<h2 id="deepscan-compliance">DeepScan for Compliance Assessments</h2>

<p>Run a <a href="../docs/deepscan.html">DeepScan</a> to generate a point-in-time security assessment of an entire repository. This is useful for:</p>

<ul>
  <li>Initial onboarding - establishing a security baseline when connecting a repository</li>
  <li>Pre-audit preparation - generating comprehensive findings reports ahead of an audit</li>
  <li>Regulatory submissions - providing evidence of security review for compliance certifications</li>
  <li>Periodic assessments - quarterly or annual full-repository reviews beyond continuous PR scanning</li>
</ul>


<h2 id="sbom-generation">SBOM Generation</h2>

<h2 id="what-is-sbom">What Is an SBOM?</h2>

<p>A Software Bill of Materials (SBOM) is a formal inventory of all the components in a software product - every library, package, framework, and dependency, along with version information and provenance data. SBOMs have become an important tool for supply chain security, enabling organizations to quickly determine whether they're affected when a new vulnerability is disclosed in a widely-used library.</p>

<p>Regulatory frameworks and government procurement requirements increasingly mandate SBOM production. Executive Order 14028 in the United States requires SBOM from software vendors selling to the federal government. Similar requirements are emerging in the EU and other jurisdictions. Even organizations not subject to regulatory mandates benefit from the visibility SBOMs provide into their software supply chain.</p>

<h2 id="sbom-with-dryrun">SBOM with DryRun Security</h2>

<p>DryRun Security generates SBOMs as a natural output of its dependency scanning capability. Because DryRun Security already analyzes your dependency manifests and lock files on every scan, the data needed for SBOM production is continuously maintained and up to date.</p>

<p>SBOMs can be exported in industry-standard formats, enabling integration with vulnerability management platforms, procurement systems, and compliance tools that consume SBOM data.</p>

<h2 id="ai-bom">AI-BOM: Bill of Materials for AI Components</h2>

<p>As AI-generated code and AI-powered libraries become prevalent in modern software, a new challenge emerges: understanding what AI components are present in your software and what their provenance is. DryRun Security generates <strong>AI-BOMs</strong> - bills of materials specifically tracking AI-originated components and AI library dependencies.</p>

<p>An AI-BOM captures:</p>
<ul>
  <li>AI and ML libraries present in the codebase and their versions</li>
  <li>Model dependencies and third-party AI service integrations</li>
  <li>Sections of code identified as AI-generated (via DryRun's AI coding visibility capability)</li>
</ul>

<h2 id="compliance-readiness">Compliance and Audit Readiness</h2>

<p>SBOM and AI-BOM data produced by DryRun Security can be provided directly to auditors, customers, or regulators as evidence of supply chain visibility and control. Combined with DryRun Security's continuous vulnerability scanning and risk trending, this provides the documented, traceable security program that compliance frameworks require.</p>
''',
}

PAGES['permissions'] = {
    'title': 'Permissions',
    'description': 'Manage roles, access controls, and permissions for DryRun Security.',
    'section': 'Platform',
    'content': '''
<h2 id="overview">Overview</h2>

<p>DryRun Security uses a role-based access control model that maps to your existing source code management platform permissions. This ensures that your security workflow respects the same access boundaries as your development workflow.</p>

<h2 id="role-mapping">Role Mapping</h2>

<p>DryRun Security automatically inherits permissions from your SCM platform:</p>

<table>
  <thead>
    <tr>
      <th>SCM Role</th>
      <th>DryRun Security Access</th>
      <th>Capabilities</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Organization Owner</strong></td>
      <td>Admin</td>
      <td>Full access to all settings, configurations, policies, and billing.</td>
    </tr>
    <tr>
      <td><strong>Repository Admin</strong></td>
      <td>Manager</td>
      <td>Configure scanning settings, manage policies, view findings, tune results for managed repositories.</td>
    </tr>
    <tr>
      <td><strong>Developer / Maintainer</strong></td>
      <td>Contributor</td>
      <td>View findings on their PRs, provide feedback on findings, access remediation guidance.</td>
    </tr>
    <tr>
      <td><strong>Read-only</strong></td>
      <td>Viewer</td>
      <td>View scan results and dashboards. No configuration or feedback access.</td>
    </tr>
  </tbody>
</table>

<h2 id="github-permissions">GitHub Permissions</h2>

<p>The DryRun Security GitHub App requests the following permissions during installation:</p>

<ul>
  <li><strong>Repository contents</strong> (read) - Required to analyze code in pull requests and repositories.</li>
  <li><strong>Pull requests</strong> (read/write) - Required to post review comments and status checks.</li>
  <li><strong>Checks</strong> (read/write) - Required to report scan results as check runs.</li>
  <li><strong>Metadata</strong> (read) - Required to list repositories and basic organization information.</li>
</ul>

<h2 id="gitlab-permissions">GitLab Permissions</h2>

<p>For GitLab integration, the Group Access Token used during setup requires:</p>

<ul>
  <li><strong>api</strong> scope - Required for merge request comments and status updates.</li>
  <li><strong>read_repository</strong> scope - Required to analyze code.</li>
  <li>The token must have at least the <strong>Maintainer</strong> role.</li>
</ul>

<h2 id="configuration-access">Configuration Access</h2>

<p>Developer edit rights have been removed for configurations. Only <strong>Admins</strong> (Organization Owners and Repository Admins mapped to Manager or above) can modify configurations in the DryRun Security dashboard. Developers retain view access to findings and can provide feedback on their PRs, but cannot change scanning configurations, policies, or blocking settings.</p>

<p>If you have a developer who is not a GitHub or GitLab admin but needs to modify configurations, contact DryRun Security support at <a href="mailto:hi@dryrun.security">hi@dryrun.security</a> to request an override.</p>

<h2 id="managing-access">Managing Access</h2>

<p>To manage who has access to DryRun Security:</p>

<ol>
  <li>Manage team members through your SCM platform - DryRun Security automatically syncs permissions.</li>
  <li>Use the DryRun Security dashboard to view current team members and their access levels.</li>
  <li>Repository-level configurations are only accessible to users with Manager or Admin access.</li>
</ol>
''',
}

PAGES['mcp'] = {
    'title': 'MCP',
    'description': 'Connect AI assistants to DryRun Security insights using the Model Context Protocol for natural language queries about your security data.',
    'section': 'Platform',
    'content': '''
<p>The DryRun Security Insights MCP enables AI assistants to securely connect to your organization's security data for powerful, context-aware code analysis. Think of it as "USB-C for AI" - a standard way for agents to interact with security insights, trends, and context across your codebase.</p>


<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/mcp/01-mcp-setup.png" alt="DryRun Security MCP Integration setup" loading="lazy"></figure>

<h2 id="what-is-the-insights-mcp">What Is the Insights MCP?</h2>

<p>The <strong>Insights MCP</strong> is a <a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer">Model Context Protocol</a> server that exposes DryRun Security's rich security analysis to AI applications. Once connected, tools like Claude Desktop or other MCP-compatible clients can answer natural language questions about security posture, pull request vulnerabilities, Code Security Agent trends, and more.</p>

<h2 id="capabilities">Capabilities</h2>

<p>With the Insights MCP connected, AI assistants can:</p>
<ul>
  <li><strong>Daily Security Summaries</strong> - Generate summaries of recent security activity over any 30-day window.</li>
  <li><strong>Pull Request Analysis</strong> - Deep-dive into the security implications of a specific pull request.</li>
  <li><strong>File Security History</strong> - View the historical security context and findings for a specific file.</li>
  <li><strong>Natural Language Search</strong> - Ask questions like: "Have any new payment integrations been introduced in the last week?"</li>
  <li><strong>Code Security Agent Stats</strong> - View counts and types of security issues across your org.</li>
  <li><strong>Trend Monitoring</strong> - Track security posture over time.</li>
</ul>

<h2 id="configuration">Configuration</h2>

<p><strong>Note:</strong> At this time, only GitHub users are supported. GitLab support is actively being implemented.</p>

<h3 id="quick-setup">Quick Setup from the Dashboard</h3>

<p>The fastest way to connect is through <strong>Settings &gt; Integrations</strong> in the DryRun Security dashboard. Each supported tool has a card with a <strong>Connect</strong> button that provides the exact command or configuration for that tool. See <a href="./ai-coding-integration.html">AI Coding Tool Integrations</a> for the full list of supported tools.</p>

<h3 id="claude-code">Claude Code (CLI)</h3>

<pre><code>claude mcp add --transport http dryrun-security   https://insights-mcp.dryrun.security/api/insights/mcp   --header "Authorization: Bearer &lt;dryrunsec_token&gt;"</code></pre>

<p>Replace <code>&lt;dryrunsec_token&gt;</code> with your token from <strong>Settings &gt; Access Keys</strong>.</p>

<h3 id="claude-desktop">Claude Desktop or Claude Web</h3>

<ol>
  <li>Navigate to <a href="https://claude.ai" target="_blank" rel="noopener noreferrer">https://claude.ai</a>.</li>
  <li>Select <strong>Settings</strong>.</li>
  <li>Select <strong>Connectors</strong>.</li>
  <li>Click <strong>Add custom connector</strong>.</li>
  <li>Enter the URL: <code>https://insights-mcp.dryrun.security/api/insights/mcp</code></li>
  <li>Select <strong>Add</strong>.</li>
</ol>

<h3 id="direct-http">Direct HTTP Configuration</h3>

<p>For clients that support HTTP-based MCP servers, use this JSON configuration:</p>

<pre><code>{
  "mcpServers": {
    "dryrun-security": {
      "type": "http",
      "url": "https://insights-mcp.dryrun.security/api/insights/mcp",
      "headers": {
        "Authorization": "Bearer &lt;dryrunsec_token&gt;"
      }
    }
  }
}</code></pre>

<h3 id="cursor-notice">Cursor Compatibility Notice</h3>

<p><strong>Known issue:</strong> Cursor currently has a known bug in its MCP implementation that may cause authentication failures. Contact <a href="mailto:hi@dryrun.security">hi@dryrun.security</a> if you need the workaround enabled for your environment.</p>

<h3 id="mcp-remote">Using mcp-remote (Fallback)</h3>

<p>For clients that don't support HTTP-based MCP servers or if you experience authentication issues, use <a href="https://github.com/geelen/mcp-remote" target="_blank" rel="noopener noreferrer">mcp-remote</a>. Requires Node.js.</p>

<pre><code>{
  "mcpServers": {
    "dryrun-security": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://insights-mcp.dryrun.security/api/insights/mcp",
        "--transport", "http-first",
        "--allow-http"
      ],
      "env": {
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}</code></pre>

<h2 id="authorization">Authorization</h2>

<p>The recommended method for connecting to the Insights MCP is using an <strong><a href="../docs/api-access-keys.html">API Access Key</a></strong>. Generate an API Access Key from <strong>Settings &gt; Access Keys</strong> in the DryRun Security dashboard and pass it as a Bearer token in the <code>Authorization</code> header. This is the best practice method for all MCP connections. See <a href="./dryrun-api.html">API Usage Guide</a> for details on key management.</p>

<p><strong>Note:</strong> At this time, only GitHub users are supported. GitLab support is actively being implemented.</p>

<h2 id="remediation-skill">DryRun Remediation Skill</h2>

<p>In addition to connecting the Insights MCP, you can install the <strong>DryRun remediation skill</strong> into supported AI coding tools. The skill enables the tool to discover security findings and generate fixes directly. For Claude Code:</p>

<pre><code>/plugin marketplace add DryRunSecurity/external-plugin-marketplace
/plugin install dryrun-remediation@dryrunsecurity</code></pre>

<p>Use the <strong>Add Skill</strong> button on the Integrations page for tool-specific instructions.</p>

<h2 id="verifying">Verifying the Connection</h2>

<p>Once configured, confirm the DryRun Security Insights tool is available in your AI assistant's toolset. Try asking: <em>"What is my insights summary for the past week?"</em></p>

<p>If you encounter any issues, reach out at <a href="mailto:hi@dryrun.security">hi@dryrun.security</a>.</p>
''',
}

PAGES['dryrun-api'] = {
    'title': 'DryRun API',
    'description': 'Programmatic access to DryRun Security findings, scans, configurations, and insights via the Simple API.',
    'section': 'Platform',
    'content': '''
<h2 id="dryrun-simple-api">DryRun Simple API</h2>

<p>The DryRun Simple API provides programmatic access to your organization's security data - findings, scans, deepscans, configurations, repositories, and insights.</p>

<ul>
  <li><strong>Swagger UI:</strong> <a href="https://simple-api.dryrun.security/api-docs/index.html" target="_blank" rel="noopener noreferrer">https://simple-api.dryrun.security/api-docs/index.html</a></li>
  <li><strong>OpenAPI (v3.0) spec:</strong> <a href="https://simple-api.dryrun.security/api-docs/v1/swagger.yaml" target="_blank" rel="noopener noreferrer">https://simple-api.dryrun.security/api-docs/v1/swagger.yaml</a></li>
  <li><strong>Base URL:</strong> <code>https://simple-api.dryrun.security/v1</code></li>
</ul>

<h2 id="authentication">Authentication</h2>

<p>All API requests require an API key generated from the DryRun Security dashboard.</p>

<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/api-guide/02-swagger.png" alt="DryRun Security API Swagger documentation" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/api-guide/01-api-key.png" alt="API key generation in DryRun Security Settings" loading="lazy"></figure>

<h3 id="getting-an-api-key">Getting an API Key</h3>

<p>Navigate to <strong>Settings &gt; Access Keys</strong> in the sidebar at <a href="https://app.dryrun.security/settings/access-keys" target="_blank" rel="noopener noreferrer">app.dryrun.security</a>. The Access Keys page provides two sections:</p>

<ul>
  <li><strong>API Keys</strong> - Create and manage API keys for your applications. Click <strong>+ Generate New API Key</strong> to create a new key.</li>
  <li><strong>Your API Keys</strong> - View and manage your existing API keys. You can revoke any key at any time.</li>
</ul>

<div class="callout callout-warning">
  <strong>Keep your API keys secure.</strong> Treat API keys like passwords. Never share them in public repositories, client-side code, or unsecured locations. If a key is compromised, revoke it immediately from the Access Keys page.
</div>

<p>The API key must be scoped to at least one account. One API key can be used to access more than one account. After creating the key, copy it to a safe place - it will not be shown again.</p>

<h3 id="using-your-api-key">Using Your API Key</h3>

<p>Send your API key in the <code>Authorization</code> header using the <code>Bearer</code> scheme:</p>

<pre><code>Authorization: Bearer dryrunsec_**********************</code></pre>

<h2 id="quick-start">Quick Start</h2>

<p>Most endpoints are scoped to an account. You'll need:</p>
<ul>
  <li><code>account_id</code> - provided by the DryRun Security platform (e.g., <code>12345678-1234-1234-1234-1234567890ab</code>)</li>
  <li><code>repository_id</code> - a UUID for a repository</li>
</ul>

<p>Typical workflow:</p>
<ol>
  <li>List your accessible accounts.</li>
  <li>Pick an account, then list repositories in that account.</li>
  <li>Use repository IDs to fetch scans and findings.</li>
</ol>

<pre><code>curl \
  -H "Authorization: Bearer $DRYRUN_API_KEY" \
  https://simple-api.dryrun.security/v1/accounts</code></pre>

<h2 id="endpoint-reference">Endpoint Reference</h2>

<h3 id="accounts">Accounts</h3>

<p><code>GET /v1/accounts</code> - List all accounts accessible by the API key.</p>

<h3 id="repositories">Repositories</h3>

<p><code>GET /v1/accounts/{account_id}/repositories</code> - List all repositories for an account.</p>

<h3 id="scans">Scans</h3>

<p><code>GET /v1/accounts/{account_id}/repositories/{repository_id}/scans</code> - List PR scans for a repository (supports filtering by status, date, and pagination).</p>

<p><code>GET /v1/accounts/{account_id}/repositories/{repository_id}/scans/{id}</code> - Get detailed PR scan results including findings.</p>

<h3 id="findings">Findings</h3>

<p><code>GET /v1/accounts/{account_id}/repositories/{repository_id}/findings</code> - List all PR findings for a repository. Each finding includes a <code>dashboard_url</code> to view it in the DryRun Security dashboard.</p>

<h3 id="deepscans">Deepscans</h3>

<p><code>GET /v1/accounts/{account_id}/deepscans</code> - List all deepscans for an account.</p>

<p><code>GET /v1/accounts/{account_id}/repositories/{repository_id}/deepscans</code> - List deepscans for a repository.</p>

<p><code>GET /v1/accounts/{account_id}/repositories/{repository_id}/deepscans/{deepscan_id}/results</code> - List findings for a specific deepscan.</p>

<h3 id="configurations-api">Configurations</h3>

<p><code>GET /v1/accounts/{account_id}/configurations</code> - List configurations for an account.</p>
<p><code>POST /v1/accounts/{account_id}/configurations</code> - Create a new configuration.</p>
<p><code>PUT /v1/accounts/{account_id}/configurations/{id}</code> - Update a configuration.</p>
<p><code>DELETE /v1/accounts/{account_id}/configurations/{id}</code> - Delete a configuration.</p>

<h3 id="analyzers-api">Analyzers</h3>

<p><code>GET /v1/accounts/{account_id}/analyzers</code> - List available analyzers. Use the <code>slug</code> field as the key in configuration analyzer settings.</p>

<h3 id="custom-policies-api">Custom Policies</h3>

<p><code>GET /v1/accounts/{account_id}/custom_policies</code> - List all Custom Code Policies for an account.</p>

<h3 id="insights-api">Insights</h3>

<p><code>GET /v1/accounts/{account_id}/insights</code> - Retrieve the daily insights digest. Insights are generated daily and highlight important security changes. Supports a <code>date</code> query parameter (YYYY-MM-DD).</p>

<h2 id="conventions">Conventions</h2>

<ul>
  <li><strong>IDs and scoping:</strong> <code>account_id</code> is required for most endpoints. <code>repository_id</code> is required for repository-scoped endpoints.</li>
  <li><strong>Response shape:</strong> Most list endpoints return a top-level <code>data</code> array.</li>
  <li><strong>Errors:</strong> If an item is not found, endpoints return <code>404</code> with <code>{"error": "not found"}</code>.</li>
</ul>

<h2 id="support">Support</h2>

<p>If you have questions about authentication, account access, or expected responses, contact DryRun Security support and include the endpoint URL you called, the HTTP status code, and the <code>request_id</code> header (if present).</p>
''',
}


# -- Integrations --

PAGES['slack-integration'] = {
    'title': 'Slack Integration',
    'description': 'Receive DryRun Security alerts and notifications in Slack.',
    'section': 'Integrations',
    'content': '''
<p>In this section we set up an integration webhook and use it to receive event notifications from DryRun Security. There is a dedicated Slack integration and a Generic webhook option. The configuration steps are identical for both.</p>

<p><strong>Prerequisite:</strong> You'll need to have already created a Webhook URL on the system you wish to integrate. Messages sent are JSON-formatted POST requests.</p>


<h2 id="notifications-setup-walkthrough">Notification Setup Walkthrough</h2>

<p>The Integrations page in the DryRun Security dashboard shows available notification channels.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/01-integrations.png" alt="Notification integrations page in DryRun Security" loading="lazy"></figure>

<h3 id="slack-integration">Slack Integration</h3>
<p>Connect DryRun Security to Slack for real-time security alerts.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/02-slack-setup.png" alt="Slack integration setup" loading="lazy"></figure>

<h3 id="generic-webhook">Generic Webhook</h3>
<p>Configure a generic webhook to send notifications to any HTTP endpoint.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/03-generic-webhook.png" alt="Generic webhook configuration" loading="lazy"></figure>

<h3 id="integration-scope">Integration Scope</h3>
<p>Global integrations notify on findings across all repositories in your organization.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/04-global-integration.png" alt="Global integration settings" loading="lazy"></figure>

<p>Targeted integrations notify only for specific repositories.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/05-targeted-integration.png" alt="Targeted integration settings" loading="lazy"></figure>

<h3 id="risk-triggers">Risk Level Triggers</h3>
<p>Configure which risk levels trigger notifications.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/06-risk-trigger.png" alt="Risk level trigger configuration" loading="lazy"></figure>

<p>Use the test button to validate your notification configuration.</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/07-test-notification.png" alt="Test notification button" loading="lazy"></figure>

<h3 id="webhook-format">Webhook Format</h3>
<p>Example JSON body sent by the generic webhook:</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/08-webhook-body.png" alt="Generic webhook JSON body example" loading="lazy"></figure>

<p>Example of a Slack notification message:</p>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/09-slack-message.png" alt="Slack notification message example" loading="lazy"></figure>

<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/10-notification-config.png" alt="Notification configuration overview" loading="lazy"></figure>
<figure class="docs-screenshot"><img src="{asset_prefix}assets/images/notifications/11-notification-list.png" alt="List of configured notifications" loading="lazy"></figure>

<h2 id="configure-global-integration">Configure a Global Integration</h2>

<p>A global integration works across all repositories in your organization with no additional configuration required.</p>

<ol>
  <li>Log in to the DryRun Security portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</li>
  <li>Navigate to <strong>Settings</strong>, then click <strong>Integrations</strong>.</li>
  <li>Click <strong>Details</strong> on the integration card you want to configure.</li>
  <li>In the <strong>Webhook URL</strong> box, add the URL for the target webhook to receive notifications.</li>
  <li>Choose a <strong>Risk Level</strong>. Notifications will be triggered when a change has a risk at or above the chosen level.</li>
  <li>Leave <strong>Enabled</strong> selected.</li>
  <li>Leave <strong>Global</strong> checked.</li>
  <li>Click <strong>Save</strong>.</li>
</ol>

<p>Once saved, the <strong>Test</strong> button will be enabled. Click it to send a test message to the Webhook URL to validate the setup.</p>

<h2 id="configure-targeted-integration">Configure a Targeted Integration</h2>

<p>A targeted integration can be used to receive notifications about one or more specific repositories. It must be assigned to a Configuration.</p>

<ol>
  <li>Follow steps 1–5 above.</li>
  <li>Leave <strong>Enabled</strong> selected.</li>
  <li>Uncheck the <strong>Global</strong> option. A <strong>Name</strong> box will appear - this name is used to reference the integration in a Configuration.</li>
  <li>Click <strong>Save</strong>, then click <strong>Test</strong> to validate.</li>
</ol>

<p><strong>Note:</strong> You'll need to add your webhook to a Configuration before notifications will be sent.</p>

<h2 id="add-to-configuration">Add Notification to a Configuration</h2>

<ol>
  <li>Navigate to <strong>Settings &gt; Configurations</strong>.</li>
  <li>Select the Configuration you want to edit.</li>
  <li>Toggle on <strong>Notifications Enabled</strong>.</li>
  <li>Select the desired webhook name(s) from the <strong>Integrations</strong> dropdown.</li>
  <li>Click <strong>Save</strong>.</li>
</ol>

<p>Changes in the repository that match the integration's risk level will now trigger a notification.</p>


<h2 id="slack-setup">Setting Up Slack Notifications</h2>

<p>DryRun Security can send real-time security finding notifications to your Slack workspace. This keeps your team informed about new vulnerabilities as they are discovered during PR scanning and DeepScan analysis.</p>

<h3 id="slack-channels">Recommended Channel Setup</h3>

<ul>
  <li><strong>#security-alerts</strong> - High and critical findings for immediate attention.</li>
  <li><strong>#security-digest</strong> - Daily or weekly summary of all findings.</li>
  <li><strong>#dev-security</strong> - All findings for developer visibility.</li>
</ul>
''',
}

PAGES['webhook-integration'] = {
    'title': 'Generic Webhook Integration',
    'description': 'Send DryRun Security events to any webhook endpoint for custom integrations.',
    'section': 'Integrations',
    'content': '''
<h2 id="overview">Overview</h2>

<p>DryRun Security supports generic webhook integration, allowing you to send security events to any HTTP endpoint. Use webhooks to integrate DryRun Security with custom dashboards, ticketing systems, SIEMs, or any other tool in your security workflow.</p>

<h2 id="configuring-webhooks">Configuring Webhooks</h2>

<ol>
  <li>Navigate to the <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">DryRun Security dashboard</a>.</li>
  <li>Go to <strong>Settings &gt; Integrations &gt; Webhooks</strong>.</li>
  <li>Click <strong>Add Webhook</strong>.</li>
  <li>Enter the <strong>URL</strong> of your webhook endpoint.</li>
  <li>Select which <strong>events</strong> should trigger the webhook:
    <ul>
      <li><strong>New Finding</strong> - Triggered when a new vulnerability is discovered.</li>
      <li><strong>Finding Resolved</strong> - Triggered when a finding is fixed or dismissed.</li>
      <li><strong>Scan Complete</strong> - Triggered when a PR scan or DeepScan finishes.</li>
      <li><strong>Policy Violation</strong> - Triggered when a custom code policy is violated.</li>
    </ul>
  </li>
  <li>Optionally configure a <strong>secret token</strong> for request signature verification.</li>
  <li>Click <strong>Save</strong>.</li>
</ol>

<h2 id="payload-format">Payload Format</h2>

<p>Webhook payloads are sent as HTTP POST requests with a JSON body. Each payload includes:</p>

<pre><code>{
  "event": "new_finding",
  "timestamp": "2026-01-15T10:30:00Z",
  "repository": "org/repo-name",
  "pull_request": 42,
  "finding": {
    "id": "finding-uuid",
    "severity": "high",
    "category": "xss",
    "title": "Cross-Site Scripting in user input handler",
    "file": "src/handlers/input.py",
    "line": 127,
    "description": "User input is rendered without escaping..."
  }
}</code></pre>

<h2 id="signature-verification">Signature Verification</h2>

<p>If a secret token is configured, DryRun Security includes an <code>X-DryRun-Signature</code> header with each request. The signature is computed as an HMAC-SHA256 of the request body using your secret token. Verify this signature on your server to ensure the request is authentic.</p>

<h2 id="retry-policy">Retry Policy</h2>

<p>If your endpoint returns a non-2xx status code, DryRun Security retries the webhook delivery up to 3 times with exponential backoff (1 minute, 5 minutes, 30 minutes). Failed deliveries are logged in the webhook configuration page.</p>
''',
}

PAGES['api-access-keys'] = {
    'title': 'API Access Keys',
    'description': 'Create and manage API access keys for programmatic access to DryRun Security.',
    'section': 'Integrations',
    'content': '''
<h2 id="overview">Overview</h2>

<p>API access keys allow you to authenticate with the <a href="./dryrun-api.html">DryRun API</a> for programmatic access to DryRun Security. Use API keys to integrate DryRun Security into your CI/CD pipelines, custom tooling, or automation workflows.</p>

<h2 id="creating-keys">Creating an API Key</h2>

<ol>
  <li>Navigate to the <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">DryRun Security dashboard</a>.</li>
  <li>Go to <strong>Settings &gt; API Keys</strong>.</li>
  <li>Click <strong>Generate New Key</strong>.</li>
  <li>Enter a <strong>name</strong> for the key (e.g., "CI Pipeline", "Security Dashboard").</li>
  <li>Select the <strong>scope</strong> for the key:
    <ul>
      <li><strong>Read-only</strong> - Query findings, scan results, and reports.</li>
      <li><strong>Read/Write</strong> - Trigger scans, update finding statuses, and manage configurations.</li>
    </ul>
  </li>
  <li>Click <strong>Create</strong>. The key is displayed once - copy it immediately and store it securely.</li>
</ol>

<h2 id="using-keys">Using API Keys</h2>

<p>Include your API key in the <code>Authorization</code> header of each request:</p>

<p><strong>MCP Connection (recommended):</strong> API Access Keys are the recommended best practice for connecting to the <a href="../docs/mcp.html">DryRun Security Insights MCP</a>. Use the key as a Bearer token in the Authorization header when configuring your MCP client.</p>

<pre><code>curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.dryrun.security/v1/findings</code></pre>

<h2 id="key-management">Key Management</h2>

<ul>
  <li><strong>Rotate keys regularly</strong> - Generate a new key and revoke the old one periodically.</li>
  <li><strong>Use descriptive names</strong> - Name keys after their use case for easy identification.</li>
  <li><strong>Revoke unused keys</strong> - Delete keys that are no longer in use from the API Keys settings page.</li>
  <li><strong>Never commit keys to source control</strong> - Use environment variables or secret management tools.</li>
</ul>

<h2 id="rate-limits">Rate Limits</h2>

<p>API keys are subject to rate limits to ensure platform stability. Current limits are displayed in the API Keys settings page. If you need higher limits, contact <a href="https://dryrun.security" target="_blank" rel="noopener noreferrer">DryRun Security support</a>.</p>
''',
}

PAGES['ai-coding-integration'] = {
    'title': 'AI Coding Integration',
    'description': 'Integrate DryRun Security with AI coding tools, IDEs, and AI agents.',
    'section': 'Integrations',
    'content': '''
<h2 id="ai-coding-tools">AI Coding Tool Integrations</h2>

<h2 id="security-in-your-editor">Security in Your Editor</h2>

<p>The earlier in the development process a vulnerability is caught, the cheaper it is to fix. DryRun Security's IDE integration brings security analysis into the development environment itself - the place where developers spend most of their time writing and reviewing code.</p>

<p>Rather than waiting for a PR to be opened to receive security feedback, developers with the IDE integration can get security context inline as they work - understanding the security implications of the code they're writing and the codebase they're modifying without leaving their editor.</p>

<h2 id="ai-coding-integrations">AI Coding Integrations</h2>

<p>DryRun Security integrates with the most popular AI coding tools. Each integration is available from the <strong>Settings &gt; Integrations</strong> page in the DryRun Security dashboard. Every AI coding integration provides two connection options:</p>

<ul>
  <li><strong>Connect</strong> - Connects the DryRun Insights MCP to the tool, giving its AI assistant access to your organization's security data for context-aware code analysis</li>
  <li><strong>Add Skill</strong> - Installs the DryRun remediation skill/plugin, enabling the tool to discover and fix security findings directly</li>
</ul>

<h3 id="supported-tools">Supported AI Coding Tools</h3>

<table>
  <thead>
    <tr><th>Tool</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td><strong>Cursor</strong></td><td>Connect DryRun Insights MCP to Cursor IDE for AI-powered code analysis</td></tr>
    <tr><td><strong>Codex</strong></td><td>Integrate DryRun Insights MCP with OpenAI Codex for enhanced code review</td></tr>
    <tr><td><strong>Claude Code</strong></td><td>Use DryRun Insights MCP with Claude Code for security-aware coding assistance</td></tr>
    <tr><td><strong>Windsurf</strong></td><td>Integrate DryRun Insights MCP with Windsurf IDE for AI-assisted code review</td></tr>
    <tr><td><strong>VS Code</strong></td><td>Connect DryRun Insights MCP to Visual Studio Code for AI-powered security analysis</td></tr>
  </tbody>
</table>

<h3 id="connect-flow">Connecting an AI Coding Tool</h3>

<p>Clicking <strong>Connect</strong> on a tool card provides the setup command or configuration for that tool. For example, connecting Claude Code provides this command:</p>

<pre><code>claude mcp add --transport http dryrun-security   https://insights-mcp.dryrun.security/api/insights/mcp   --header "Authorization: Bearer &lt;dryrunsec_token&gt;"</code></pre>

<p>Replace <code>&lt;dryrunsec_token&gt;</code> with your API token from <strong>Settings &gt; Access Keys</strong>. See <a href="../docs/dryrun-api.html">API Usage Guide</a> for how to generate an access key.</p>

<h3 id="add-skill-flow">Adding the Remediation Skill</h3>

<p>Clicking <strong>Add Skill</strong> installs the DryRun remediation plugin into your coding tool. For example, in Claude Code:</p>

<pre><code>/plugin marketplace add DryRunSecurity/external-plugin-marketplace
/plugin install dryrun-remediation@dryrunsecurity</code></pre>

<p>Once the skill is installed, the AI assistant can discover security findings from DryRun Security and generate fixes directly within your coding session.</p>

<h2 id="desktop-integrations">Desktop Integrations</h2>

<p>For desktop AI applications that support MCP, DryRun Security offers dedicated integration cards:</p>

<ul>
  <li><strong>Claude Desktop</strong> - Connect the DryRun Insights MCP to Claude Desktop for security-aware conversations about your codebase</li>
</ul>

<p>See <a href="./mcp.html">MCP Integration</a> for detailed configuration instructions for all supported clients.</p>

<h2 id="ai-native-ide">AI-Native IDE Workflows</h2>

<p>For teams using AI coding assistants, the DryRun Security integration is particularly valuable. It allows the AI assistant to query DryRun Security's security intelligence as part of code generation - helping AI assistants write more secure code by understanding what vulnerabilities have been found in the codebase and what security patterns are in use.</p>

<p>This is especially relevant as teams adopt <code>AGENTS.md</code> to guide AI coding agents. See <a href="./repository-context.html">AGENTS.md</a> for how to configure security guidelines that AI agents and DryRun Security both use.</p>


<h2 id="ai-tool-integrations">AI Tool Integrations</h2>

<h2 id="ai-generated-code-coverage">AI-Generated Code Coverage</h2>

<p>DryRun Security reviews all code in every pull request, regardless of whether it was written by a human or generated by an AI coding tool. No special configuration or setup is needed - if the code reaches a PR, DryRun analyzes it with the same <a href="../docs/security-reviews.html">Contextual Security Analysis</a> applied to all changes.</p>

<p>This is important because AI coding assistants are generating an increasing share of production code, and AI-generated code carries its own patterns of security risk.</p>

<h2 id="compatible-tools">Compatible AI Coding Tools</h2>

<p>DryRun Security works with any tool that produces code submitted through a pull request or merge request:</p>

<ul>
  <li><strong>GitHub Copilot</strong> - inline code suggestions and chat-based generation</li>
  <li><strong>Cursor</strong> - AI-native code editor with multi-file generation</li>
  <li><strong>Windsurf</strong> - AI coding assistant</li>
  <li><strong>OpenAI Codex</strong> - code generation API and CLI</li>
  <li><strong>Claude Code</strong> - Anthropic's coding assistant</li>
  <li><strong>Amazon CodeWhisperer</strong> - AWS coding companion</li>
  <li><strong>Any other tool</strong> that generates code committed to a Git repository</li>
</ul>

<p>Because DryRun operates at the SCM level (analyzing PRs), compatibility with new AI tools is automatic. There is no integration required on the AI tool side.</p>

<h2 id="common-ai-patterns">Common AI-Generated Code Risks</h2>

<p>AI coding tools tend to produce specific patterns of security issues that DryRun's analyzers are particularly effective at catching:</p>

<ul>
  <li><strong>Missing input validation</strong> - AI-generated endpoints that accept and use user input without sanitization</li>
  <li><strong>Hardcoded credentials</strong> - example API keys and tokens that should have been replaced with environment variables</li>
  <li><strong>Incomplete authorization</strong> - CRUD operations generated without access control checks</li>
  <li><strong>Outdated patterns</strong> - AI models trained on older code that uses deprecated or insecure APIs</li>
  <li><strong>Copy-paste vulnerabilities</strong> - code generated from training data that contains known vulnerability patterns</li>
</ul>

<h2 id="visibility-into-ai-changes">Visibility into AI-Generated Changes</h2>

<p>DryRun Security's <a href="../docs/ai-coding-integration.html">AI Coding Visibility</a> feature provides observability into how AI tools are being used across your codebase - which repositories have the most AI-generated code, what types of changes are being made, and where security findings correlate with AI-generated contributions.</p>

<h2 id="mcp-workflows">MCP for Agentic Workflows</h2>

<p>For teams using AI coding agents that operate autonomously (creating PRs, making multi-file changes), DryRun Security's <a href="../docs/mcp.html">MCP integration</a> enables the agent to query security status, check findings, and respond to security feedback programmatically. This creates a closed loop where AI agents can fix their own security issues before a human reviews the PR.</p>

<h2 id="related-pages-ai-tools">Related Pages</h2>

<ul>
  <li><a href="../docs/ai-coding-integration.html">Securing AI-Generated Code</a> - DryRun's approach to AI code security</li>
  <li><a href="../docs/ai-coding-integration.html">AI Coding Visibility</a> - observability into AI-generated changes</li>
  <li><a href="../docs/ai-coding-integration.html">Malicious Agent Detection</a> - detecting adversarial AI behavior</li>
  <li><a href="../docs/mcp.html">MCP Integration</a> - programmatic access for AI agents</li>
</ul>


<h2 id="securing-ai-code">Securing AI-Generated Code</h2>

<h2 id="the-ai-code-security-challenge">The AI Code Security Challenge</h2>

<p>AI coding assistants - GitHub Copilot, Cursor, Claude Code, and similar tools - have dramatically changed how software is written. Developers using these tools can produce working code faster than ever before. But AI-generated code introduces a new and underappreciated security challenge: AI models can produce code that is functionally correct and syntactically sound while containing security vulnerabilities that the developer who accepted the suggestion didn't introduce and may not recognize.</p>

<p>Traditional code review processes assume the developer is responsible for the code they write. AI-generated code muddies this: the developer accepted a suggestion but didn't reason through every security implication of the code that was generated. The responsibility is shared - and the security tooling needs to account for this new dynamic.</p>

<h2 id="how-dryrun-handles-ai-generated-code">How DryRun Security Handles AI-Generated Code</h2>

<p>DryRun Security applies additional analytical scrutiny to code that exhibits characteristics of AI generation. This isn't about penalizing AI-assisted development - it's about recognizing that AI-generated code patterns, particularly around security-sensitive operations, warrant extra care in review.</p>

<p>AI coding assistants sometimes:</p>
<ul>
  <li>Generate code that uses deprecated or insecure API patterns that were common in their training data</li>
  <li>Produce authentication and authorization logic that is structurally plausible but subtly flawed</li>
  <li>Include hardcoded credentials or placeholder values that developers inadvertently ship</li>
  <li>Generate SQL queries or shell commands that are vulnerable to injection in the specific context of the application</li>
</ul>

<p>DryRun Security's contextual analysis is particularly effective at catching these issues because it evaluates AI-generated code in the same way it evaluates human-written code: with full understanding of the surrounding context, data flows, and security-relevant patterns.</p>

<h2 id="organizational-visibility">Organizational Visibility</h2>

<p>Beyond per-PR security analysis, DryRun Security provides visibility into AI coding activity across your organization - tracking where AI-generated code is being introduced and what security implications it carries. See <a href="./ai-coding-integration.html">AI Coding Visibility</a> for details.</p>


<h2 id="ai-coding-visibility">AI Coding Visibility</h2>

<h2 id="understanding-ai-in-your-codebase">Understanding AI in Your Codebase</h2>

<p>When AI coding assistants are widely adopted across an engineering organization, a natural question emerges: how much of our codebase was written by AI, and does that matter for security? The answer to the second question is increasingly yes - and answering the first requires dedicated tooling.</p>

<p>DryRun Security's AI Coding Visibility capability gives security teams and engineering leadership an organizational view of AI coding activity: where AI-generated code is being introduced, at what rate, in which repositories and by which teams, and what the security characteristics of that code are.</p>

<h2 id="what-ai-coding-visibility-tracks">What AI Coding Visibility Tracks</h2>

<p>AI Coding Visibility provides insight across several dimensions:</p>

<ul>
  <li><strong>AI code volume</strong> - What percentage of new code being committed exhibits characteristics of AI generation? How is this changing over time as AI adoption grows or changes in your organization?</li>
  <li><strong>Distribution across repositories</strong> - Are some teams or projects using AI coding assistants more than others? Are security findings concentrated in AI-heavy repositories?</li>
  <li><strong>Finding rates by code origin</strong> - Do AI-generated code sections have systematically different security finding rates compared to human-written code? Understanding this helps calibrate review processes and training investments.</li>
  <li><strong>Agent activity patterns</strong> - In environments using autonomous AI coding agents (not just suggestion-based assistants), visibility into what the agents are doing, what files they're modifying, and what patterns emerge in their changes.</li>
</ul>

<h2 id="security-implications">Security Implications for Security Teams</h2>

<p>This visibility serves several practical security use cases:</p>

<ul>
  <li><strong>Risk concentration</strong> - Identify whether certain areas of the codebase or certain development patterns are producing disproportionate security risk from AI-generated code.</li>
  <li><strong>Audit trail</strong> - For regulated industries, maintaining a record of AI involvement in code production is increasingly an audit requirement.</li>
  <li><strong>Supply chain transparency</strong> - AI-BOM generation (see <a href="../compliance-grc.html">SBOM Generation</a>) provides a formal record of AI involvement in software production for compliance purposes.</li>
  <li><strong>Policy enforcement</strong> - Custom Code Policies can be configured specifically for AI-generated code sections, enforcing stricter review criteria where AI involvement is detected.</li>
</ul>


<h2 id="malicious-agent-detection">Malicious Agent Detection</h2>

<h2 id="the-malicious-agent-threat">The Malicious Agent Threat</h2>

<p>As AI coding agents become more capable and more autonomous, they introduce a novel threat vector: an AI agent that has been compromised, manipulated via prompt injection, or is operating outside its intended parameters can introduce malicious code directly into a codebase. Unlike a human developer inserting malicious code, a compromised AI agent can do so at scale, across multiple repositories, in ways that may be difficult to distinguish from legitimate AI-assisted development.</p>

<p>This is not a theoretical concern. Prompt injection attacks against coding agents have been demonstrated in research settings, and as AI agents gain broader permissions in development environments, the potential impact of such attacks grows.</p>

<h2 id="what-dryrun-detects">What DryRun Security Detects</h2>

<p>DryRun Security's malicious agent detection capability is designed to identify code changes that exhibit patterns consistent with malicious intent, regardless of whether they originate from a human or an AI agent:</p>

<ul>
  <li><strong>Backdoor patterns</strong> - Code that creates covert access mechanisms, such as hardcoded credential bypass paths, undocumented administrative endpoints, or logic that behaves differently based on hidden trigger conditions.</li>
  <li><strong>Data exfiltration patterns</strong> - Code that transmits data to unexpected external endpoints or stores data in ways inconsistent with the application's intended behavior.</li>
  <li><strong>Permission escalation</strong> - Changes that expand the permissions available to the application beyond what its function requires.</li>
  <li><strong>Obfuscated logic</strong> - Code structured to obscure its intent - unusual encoding, unnecessarily complex indirection, or logic that accomplishes a simple operation through unnecessarily convoluted means.</li>
</ul>

<h2 id="behavioral-context">Behavioral Context</h2>

<p>Malicious agent detection is strengthened by DryRun Security's git behavioral analysis capability. Code changes arriving through unusual patterns - outside normal working hours, from unexpected contributors, making atypical modifications to security-sensitive files - are evaluated with elevated scrutiny. Behavioral anomalies don't trigger automatic findings, but they raise the signal strength of other analysis.</p>

<h2 id="defense-in-depth">Defense in Depth</h2>

<p>Malicious agent detection is one layer in a defense-in-depth approach to AI coding security. Combined with Custom Code Policies that enforce organizational coding standards, the Secrets Analyzer detecting credential introduction, and the code security knowledge graph tracking behavioral patterns over time, DryRun Security provides comprehensive coverage against AI-specific security risks in the development pipeline.</p>


<h2 id="ai-red-teaming">AI Red Teaming</h2>

<h2 id="threat-landscape">The AI Development Threat Landscape</h2>

<p>AI-assisted development introduces new categories of security risk that traditional tools are not designed to detect. When AI agents write code, review code, or interact with development infrastructure, they create attack surfaces that adversaries can exploit through prompt injection, supply chain manipulation, and behavioral subversion.</p>

<h2 id="attack-vectors">AI-Specific Attack Vectors</h2>

<p>DryRun Security's AI Agent Security capabilities address several categories of threats:</p>

<ul>
  <li><strong>Prompt injection via code</strong> - malicious instructions embedded in code comments, documentation, or dependency files that manipulate AI coding assistants into generating insecure code</li>
  <li><strong>Malicious agent skills</strong> - AI agents with tool access (file system, network, shell) that can be manipulated into performing unintended actions. See <a href="../docs/ai-coding-integration.html">Malicious Agent Detection</a> for details</li>
  <li><strong>Training data poisoning</strong> - AI models generating code patterns derived from intentionally vulnerable training examples</li>
  <li><strong>Supply chain attacks via AI</strong> - adversaries using AI-generated PRs to introduce subtle backdoors that pass human review</li>
</ul>

<h2 id="behavioral-analysis">Behavioral Analysis</h2>

<p>DryRun Security applies <a href="../docs/pr-variant-analysis.html">Git Behavioral Analysis</a> to detect anomalous patterns in AI-generated contributions. This includes:</p>

<ul>
  <li>Unusual commit patterns - timing, frequency, or volume that deviates from established baselines</li>
  <li>Code style anomalies - changes that do not match the repository's established patterns</li>
  <li>Scope creep - AI-generated changes that modify files or systems outside the stated scope of a task</li>
  <li>Privilege escalation attempts - changes to authorization, permissions, or access control that were not part of the original request</li>
</ul>

<h2 id="continuous-monitoring">Continuous Monitoring</h2>

<p>Rather than point-in-time assessments, DryRun Security provides continuous monitoring of AI-assisted development activity. Every PR - whether authored by a human, an AI assistant, or an autonomous agent - receives the same depth of security analysis. This means adversarial patterns are detected at the moment they appear, not during a periodic review.</p>

<h2 id="threat-modeling-support">Threat Modeling Support</h2>

<p>DryRun Security's <a href="../docs/architecture-risks.html">intelligence index</a> capabilities support threat modeling exercises by answering questions like:</p>

<ul>
  <li>"Which repositories have the most AI-generated code changes this month?"</li>
  <li>"What new API endpoints were introduced by AI-generated PRs?"</li>
  <li>"Show findings correlated with AI-generated commits across all repos"</li>
</ul>

<p>This data helps security teams prioritize review efforts and identify repositories where AI-generated code may need additional scrutiny.</p>

<h2 id="related-pages">Related Pages</h2>

<ul>
  <li><a href="../docs/ai-coding-integration.html">Malicious Agent Detection</a> - detecting adversarial AI agent behavior</li>
  <li><a href="../docs/pr-variant-analysis.html">Git Behavioral Analysis</a> - anomaly detection in commit patterns</li>
  <li><a href="../docs/ai-coding-integration.html">AI Coding Visibility</a> - observability into AI-generated changes</li>
  <li><a href="../docs/ai-coding-integration.html">Securing AI-Generated Code</a> - security analysis for AI-written code</li>
</ul>
''',
}



# ---------------------------------------------------------------------------

ORDERED_PAGES = []
for section in SECTIONS:
    for slug in section['pages']:
        ORDERED_PAGES.append(slug)


def get_section_for_slug(slug: str) -> str:
    for section in SECTIONS:
        if slug in section['pages']:
            return section['name']
    return ''


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_sidebar(current_slug: str, asset_prefix: str) -> str:
    parts = []
    parts.append('<nav class="sidebar" id="sidebar">')
    parts.append('<div class="sidebar-search">')
    parts.append('<div class="sidebar-search-wrap">')
    parts.append('<svg class="sidebar-search-icon" viewBox="0 0 20 20" fill="currentColor" width="14" height="14" aria-hidden="true"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/></svg>')
    parts.append('<input type="text" id="docsSearch" placeholder="Search docs..." autocomplete="off">')
    parts.append('<span class="sidebar-search-kbd"><kbd>&#8984;</kbd><kbd>K</kbd></span>')
    parts.append('</div>')
    parts.append('<div id="searchResults" class="search-results" hidden></div>')
    parts.append('</div>')
    parts.append('<div class="sidebar-nav">')
    for section in SECTIONS:
        parts.append('<div class="sidebar-section">')
        parts.append(f'<p class="sidebar-section-title">{esc(section["name"])}</p>')
        parts.append('<ul class="sidebar-links">')
        for slug in section['pages']:
            page = PAGES.get(slug, {})
            title = page.get('title', slug)
            active_class = ' class="active"' if slug == current_slug else ''
            parts.append(f'<li><a href="{esc(asset_prefix)}docs/{esc(slug)}.html"{active_class}>{esc(title)}</a></li>')
        parts.append('</ul>')
        parts.append('</div>')
    parts.append('</div>')
    parts.append('</nav>')
    return '\n'.join(parts)


def render_toc(toc_items: list) -> str:
    if not toc_items:
        return ''
    parts = []
    parts.append('<aside class="toc-sidebar">')
    parts.append('<p class="toc-title">On this page</p>')
    parts.append('<ul class="toc-list">')
    for item in toc_items:
        level_class = 'toc-h3' if item['level'] == 'h3' else 'toc-h2'
        parts.append(f'<li class="{esc(level_class)}"><a href="#{esc(item["anchor"])}">{esc(item["label"])}</a></li>')
    parts.append('</ul>')
    parts.append('</aside>')
    return '\n'.join(parts)


def render_prev_next(slug: str, asset_prefix: str) -> str:
    idx = ORDERED_PAGES.index(slug) if slug in ORDERED_PAGES else -1
    if idx == -1:
        return ''

    parts = ['<nav class="prev-next">']

    if idx > 0:
        prev_slug = ORDERED_PAGES[idx - 1]
        prev_page = PAGES.get(prev_slug, {})
        prev_title = prev_page.get('title', prev_slug)
        parts.append(
            f'<a href="{esc(asset_prefix)}docs/{esc(prev_slug)}.html" class="prev-next-link prev-link">'
            f'<span class="prev-next-label">← Previous</span>'
            f'<span class="prev-next-title">{esc(prev_title)}</span>'
            f'</a>'
        )
    else:
        parts.append('<span></span>')

    if idx < len(ORDERED_PAGES) - 1:
        next_slug = ORDERED_PAGES[idx + 1]
        next_page = PAGES.get(next_slug, {})
        next_title = next_page.get('title', next_slug)
        parts.append(
            f'<a href="{esc(asset_prefix)}docs/{esc(next_slug)}.html" class="prev-next-link next-link">'
            f'<span class="prev-next-label">Next →</span>'
            f'<span class="prev-next-title">{esc(next_title)}</span>'
            f'</a>'
        )

    parts.append('</nav>')
    return '\n'.join(parts)


HEADER_HTML = '''  <header class="site-header">
    <div class="header-inner">
      <div class="header-left">
        <a href="https://www.dryrun.security" target="_blank" rel="noopener noreferrer" class="logo-link">
          <svg class="logo" viewBox="0 0 450 119" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="DryRun Security"><path d="M160.284 0C176.345 0 185.949 10.3885 185.949 25.6751V25.7541C185.949 40.9616 176.345 51.3501 160.284 51.3501H140.719V0H160.284ZM148.977 43.5488H160.284C171.077 43.5488 177.612 36.2808 177.612 25.7343V25.6553C177.612 15.1285 171.057 7.78151 160.284 7.78151H148.977V43.5488Z"/><path d="M237.714 51.3501H228.406L216.94 33.9898H204.286V51.3501H196.029V0H216.485C229.357 0 236.426 6.59652 236.426 17.222V17.301C236.426 25.0826 232.407 30.6521 224.822 32.8838L237.694 51.3501H237.714ZM204.306 7.50501V26.8008H216.505C223.871 26.8008 228.189 23.6013 228.189 17.301V17.222C228.189 10.8428 223.871 7.50501 216.505 7.50501H204.306Z"/><path d="M265.893 25.1615L281.735 0H290.884L270.052 32.5678V51.3304H261.715V32.5678L240.882 0H249.952L265.873 25.1615H265.893Z"/><path d="M340.431 51.3501H331.124L319.678 33.9898H307.024V51.3501H298.766V0H319.222C332.094 0 339.164 6.59652 339.164 17.222V17.301C339.164 25.0826 335.144 30.6521 327.559 32.8838L340.431 51.3501ZM307.024 7.50501V26.8008H319.222C326.589 26.8008 330.906 23.6013 330.906 17.301V17.222C330.906 10.8428 326.589 7.50501 319.222 7.50501H307.024Z"/><path d="M385.344 0H393.681V28.4203C393.681 45.2671 383.779 52.2389 371.284 52.2389H371.205C358.709 52.2389 348.808 45.2671 348.808 28.4203V0H357.145V28.4203C357.145 40.2901 363.996 44.2203 371.205 44.2203H371.284C378.492 44.2203 385.344 40.2901 385.344 28.4203V0Z"/><path d="M441.881 0H449.921V51.3501H442.336L413.622 13.8053V51.3501H405.582V0H413.167L441.881 37.5448V0Z"/><path d="M167.314 89.4481C165.215 86.0313 161.908 84.1748 156.878 84.1748H156.819C151.472 84.1748 148.383 86.1103 148.383 89.1321C148.383 91.2848 149.591 93.1018 154.185 94.1881L162.403 96.1236C169.572 97.7826 171.572 102.503 171.513 107.342C171.513 113.938 165.71 118.066 156.898 118.066H156.839C148.898 118.066 143.274 115.044 140.68 109.475L145.749 105.841C148.007 110.679 151.809 112.615 156.957 112.615H157.017C162.423 112.615 165.294 110.423 165.294 107.164C165.294 104.458 163.75 102.542 159.829 101.496L150.838 99.2441C144.501 97.7036 142.185 93.7931 142.185 89.3493C142.185 82.4763 147.987 78.6646 157.076 78.6646H157.136C163.651 78.6646 168.384 81.0346 171.037 84.9846L167.334 89.4481H167.314Z"/><path d="M210.009 79.3164V85.0439H190.702V95.5509H208.029V101.338H190.702V111.687H210.009V117.414H184.583V79.3362H210.009V79.3164Z"/><path d="M250.566 87.6311C247.912 85.4388 244.605 84.3921 241.021 84.3921H240.961C232.842 84.3921 227.614 90.2776 227.614 98.3159V98.3751C227.674 106.512 232.902 112.358 240.961 112.358H241.021C244.882 112.358 248.031 111.193 250.566 109.119L253.932 113.741C250.506 116.723 246.15 118.086 241.021 118.086H240.961C228.981 118.086 221.475 110.047 221.475 98.3949V98.3356C221.475 86.7226 228.981 78.6843 240.961 78.6843H241.021C245.813 78.6843 250.348 79.9483 253.932 83.0293L250.566 87.6508V87.6311Z"/><path d="M292.548 79.3164H298.726V100.39C298.726 112.891 291.379 118.046 282.112 118.046H282.052C272.784 118.046 265.438 112.872 265.438 100.39V79.3164H271.616V100.39C271.616 109.198 276.686 112.121 282.052 112.121H282.112C287.458 112.121 292.548 109.198 292.548 100.39V79.3164Z"/><path d="M344.114 117.394H337.223L328.727 104.517H319.341V117.394H313.222V79.3164H328.391C337.936 79.3164 343.183 84.2144 343.183 92.0749V92.1342C343.183 97.921 340.193 102.029 334.569 103.688L344.114 117.394ZM319.341 84.8662V99.1652H328.391C333.856 99.1652 337.045 96.7952 337.045 92.1144V92.0552C337.045 87.3152 333.837 84.8464 328.391 84.8464H319.341V84.8662Z"/><path d="M356.966 117.394V79.3164H363.085V117.394H356.966Z"/><path d="M406.018 79.3164V85.2019H393.879V117.394H387.7V85.2019H375.561V79.3164H406.018Z"/><path d="M431.445 97.9802L443.208 79.3164H450L434.554 103.471V117.394H428.375V103.471L412.929 79.3164H419.662L431.465 97.9802H431.445Z"/><path d="M114.163 10.5269H107.767C107.213 10.5269 106.777 10.9614 106.777 11.5144V17.1629L72.221 76.966L62.478 58.3417L73.7854 35.9452H78.3401C78.8945 35.9452 79.3302 35.5107 79.3302 34.9577V28.5784C79.3302 28.0254 78.8945 27.5909 78.3401 27.5909H71.9437C71.3893 27.5909 70.9536 28.0254 70.9536 28.5784V30.2966H50.2992V28.5784C50.2992 28.0254 49.8636 27.5909 49.3091 27.5909H42.9128C42.3583 27.5909 41.9226 28.0254 41.9226 28.5784V34.9577C41.9226 35.5107 42.3583 35.9452 42.9128 35.9452H47.4278L59.1511 58.3615L35.7243 104.794L8.3766 52.7327V47.0249C8.3766 46.4719 7.94094 46.0374 7.38646 46.0374H0.990142C0.435663 46.0374 0 46.4719 0 47.0249V53.4042C0 53.9572 0.435663 54.3917 0.990142 54.3917H5.92105L32.4371 104.893C31.9024 104.912 31.4865 105.347 31.4865 105.88V112.259C31.4865 112.812 31.9222 113.247 32.4767 113.247H38.873C39.4275 113.247 39.8631 112.812 39.8631 112.259V105.88C39.8631 105.88 39.8631 105.821 39.8631 105.781C39.8235 105.327 39.4473 104.972 38.972 104.912L60.8343 61.6005L68.8941 77.0055C68.4386 77.0845 68.0624 77.4795 68.0624 77.9535V84.3328C68.0624 84.8858 68.498 85.3203 69.0525 85.3203H75.4489C76.0033 85.3203 76.439 84.8858 76.439 84.3328V77.9535C76.439 77.4597 76.0627 77.0647 75.6073 77.0055L109.193 18.8811H114.163C114.718 18.8811 115.154 18.4466 115.154 17.8936V11.5144C115.154 10.9614 114.718 10.5269 114.163 10.5269ZM60.7947 55.1422L50.2794 35.0367C50.2794 35.0367 50.2794 34.9972 50.2794 34.9774V33.2592H70.9338V34.9774C70.9338 34.9774 70.9338 34.9774 70.9338 34.9972L60.7749 55.1422H60.7947Z"/><path d="M9.28748 40.8627C9.12906 40.8627 8.97063 40.843 8.81221 40.7837C8.39635 40.6455 7.52503 40.3492 7.58443 39.9345C7.64384 39.4605 7.76266 39.263 7.88148 38.9075C15.8422 15.6814 37.1897 1.61938 61.8244 1.61938C76.1815 1.61938 89.291 6.1224 99.9053 15.7407C100.103 15.925 100.348 16.2081 100.638 16.5899C100.876 16.8862 100.262 17.5182 100.004 17.8144C99.4499 18.4267 98.5191 18.4662 97.925 17.9132C87.8652 8.78865 75.4488 4.56214 61.8244 4.56214C38.4571 4.56214 19.684 17.9724 10.6737 39.8752C10.436 40.4677 9.88157 40.8627 9.28748 40.8627Z" fill="#38D92D"/><path d="M26.219 103.944C25.9022 103.865 25.5259 103.609 25.2487 103.391C13.4066 93.6745 6.03995 79.9679 4.53493 64.8197C4.49533 64.4839 4.3369 63.6939 4.61414 63.5359C4.9904 63.3186 5.36665 63.2594 5.84192 63.2199C6.63403 63.1014 7.36674 63.7334 7.46575 64.5432C8.91136 78.9212 15.9018 91.9167 27.13 101.14C27.7637 101.653 27.8231 102.443 27.3082 103.075C27.0112 103.431 26.5161 103.865 26.219 103.984V103.944Z" fill="#38D92D"/><path d="M61.8245 116.446C56.5966 116.446 51.4281 115.755 46.4575 114.372C46.1011 114.274 45.7446 114.214 45.3684 113.977C44.9921 113.74 45.309 112.99 45.4278 112.555C45.6456 111.765 46.4575 111.311 47.2497 111.528C51.9627 112.832 56.8738 113.484 61.8245 113.484C91.9447 113.484 116.441 89.0529 116.441 59.0131C116.441 49.1776 114.262 41.3171 109.233 32.9233C108.817 32.2321 108.916 31.0471 109.708 30.5533C110.104 30.2966 110.322 30.1386 110.678 30.0793C110.975 30.0398 111.431 30.7113 111.609 31.0076C116.896 39.8556 119.391 48.6641 119.391 59.0329C119.391 90.6922 93.5685 116.446 61.8245 116.446Z" fill="#38D92D"/><path d="M35.6254 93.0228L53.1113 58.0653L44.4574 41.3172H38.4968C37.6056 41.3172 36.8927 40.6062 36.8927 39.7175V23.7792C36.8927 22.8904 37.6056 22.1794 38.4968 22.1794H82.7165C83.6077 22.1794 84.3206 22.8904 84.3206 23.7792V39.7372C84.3206 40.626 83.6077 41.337 82.7165 41.337H76.7955L68.4783 57.9665L72.5181 65.7678L97.2914 22.9102C88.1425 13.9832 75.6469 8.4729 61.8443 8.4729C37.467 8.4729 17.1295 25.6357 12.258 48.4865L35.6452 93.0228H35.6254Z" fill="#38D92D"/><path d="M81.8649 76.9266V89.1518C81.8649 90.0406 81.152 90.7516 80.2609 90.7516H64.28C63.3889 90.7516 62.676 90.0406 62.676 89.1518V76.6105L60.8739 73.1148L44.1801 106.473C49.6655 108.507 55.6064 109.613 61.8046 109.613C89.8059 109.613 112.5 86.9793 112.5 59.0528C112.5 50.2245 110.223 41.9295 106.242 34.7207L81.8451 76.9463L81.8649 76.9266Z" fill="#38D92D"/></svg>
        </a>
        <div class="header-divider"></div>
        <nav class="header-nav">
          <a href="https://www.dryrun.security/product/sast" target="_blank" rel="noopener noreferrer">Product</a>
          <a href="https://www.dryrun.security/blog" target="_blank" rel="noopener noreferrer">Blog</a>
          <a href="{asset_prefix}index.html">Docs</a>
          <a href="https://www.dryrun.security/faqs" target="_blank" rel="noopener noreferrer">FAQ</a>
        </nav>
      </div>
      <div class="header-right">
        <button class="theme-toggle" id="themeToggle" aria-label="Toggle light/dark mode">
          <svg class="icon-sun" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="4"/>
            <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/>
          </svg>
          <svg class="icon-moon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
        <button class="sidebar-toggle" id="sidebarToggle" aria-label="Toggle navigation">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M3 5h14M3 10h14M3 15h14"/>
          </svg>
        </button>
        <a href="https://www.dryrun.security/get-started" target="_blank" rel="noopener noreferrer" class="btn-get-started">Get Started</a>
        <a href="https://www.dryrun.security/get-a-demo" target="_blank" rel="noopener noreferrer" class="btn-demo">Get a Demo</a>
      </div>
    </div>
  </header>'''

FOOTER_HTML = '''  <footer class="site-footer">
    <div class="footer-main">
      <div class="footer-grid">
        <div class="footer-col footer-col-logo">
          <a href="https://www.dryrun.security" target="_blank" rel="noopener noreferrer">
            <svg class="footer-logo-img" viewBox="0 0 450 119" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="DryRun Security"><path d="M160.284 0C176.345 0 185.949 10.3885 185.949 25.6751V25.7541C185.949 40.9616 176.345 51.3501 160.284 51.3501H140.719V0H160.284ZM148.977 43.5488H160.284C171.077 43.5488 177.612 36.2808 177.612 25.7343V25.6553C177.612 15.1285 171.057 7.78151 160.284 7.78151H148.977V43.5488Z"/><path d="M237.714 51.3501H228.406L216.94 33.9898H204.286V51.3501H196.029V0H216.485C229.357 0 236.426 6.59652 236.426 17.222V17.301C236.426 25.0826 232.407 30.6521 224.822 32.8838L237.694 51.3501H237.714ZM204.306 7.50501V26.8008H216.505C223.871 26.8008 228.189 23.6013 228.189 17.301V17.222C228.189 10.8428 223.871 7.50501 216.505 7.50501H204.306Z"/><path d="M265.893 25.1615L281.735 0H290.884L270.052 32.5678V51.3304H261.715V32.5678L240.882 0H249.952L265.873 25.1615H265.893Z"/><path d="M340.431 51.3501H331.124L319.678 33.9898H307.024V51.3501H298.766V0H319.222C332.094 0 339.164 6.59652 339.164 17.222V17.301C339.164 25.0826 335.144 30.6521 327.559 32.8838L340.431 51.3501ZM307.024 7.50501V26.8008H319.222C326.589 26.8008 330.906 23.6013 330.906 17.301V17.222C330.906 10.8428 326.589 7.50501 319.222 7.50501H307.024Z"/><path d="M385.344 0H393.681V28.4203C393.681 45.2671 383.779 52.2389 371.284 52.2389H371.205C358.709 52.2389 348.808 45.2671 348.808 28.4203V0H357.145V28.4203C357.145 40.2901 363.996 44.2203 371.205 44.2203H371.284C378.492 44.2203 385.344 40.2901 385.344 28.4203V0Z"/><path d="M441.881 0H449.921V51.3501H442.336L413.622 13.8053V51.3501H405.582V0H413.167L441.881 37.5448V0Z"/><path d="M167.314 89.4481C165.215 86.0313 161.908 84.1748 156.878 84.1748H156.819C151.472 84.1748 148.383 86.1103 148.383 89.1321C148.383 91.2848 149.591 93.1018 154.185 94.1881L162.403 96.1236C169.572 97.7826 171.572 102.503 171.513 107.342C171.513 113.938 165.71 118.066 156.898 118.066H156.839C148.898 118.066 143.274 115.044 140.68 109.475L145.749 105.841C148.007 110.679 151.809 112.615 156.957 112.615H157.017C162.423 112.615 165.294 110.423 165.294 107.164C165.294 104.458 163.75 102.542 159.829 101.496L150.838 99.2441C144.501 97.7036 142.185 93.7931 142.185 89.3493C142.185 82.4763 147.987 78.6646 157.076 78.6646H157.136C163.651 78.6646 168.384 81.0346 171.037 84.9846L167.334 89.4481H167.314Z"/><path d="M210.009 79.3164V85.0439H190.702V95.5509H208.029V101.338H190.702V111.687H210.009V117.414H184.583V79.3362H210.009V79.3164Z"/><path d="M250.566 87.6311C247.912 85.4388 244.605 84.3921 241.021 84.3921H240.961C232.842 84.3921 227.614 90.2776 227.614 98.3159V98.3751C227.674 106.512 232.902 112.358 240.961 112.358H241.021C244.882 112.358 248.031 111.193 250.566 109.119L253.932 113.741C250.506 116.723 246.15 118.086 241.021 118.086H240.961C228.981 118.086 221.475 110.047 221.475 98.3949V98.3356C221.475 86.7226 228.981 78.6843 240.961 78.6843H241.021C245.813 78.6843 250.348 79.9483 253.932 83.0293L250.566 87.6508V87.6311Z"/><path d="M292.548 79.3164H298.726V100.39C298.726 112.891 291.379 118.046 282.112 118.046H282.052C272.784 118.046 265.438 112.872 265.438 100.39V79.3164H271.616V100.39C271.616 109.198 276.686 112.121 282.052 112.121H282.112C287.458 112.121 292.548 109.198 292.548 100.39V79.3164Z"/><path d="M344.114 117.394H337.223L328.727 104.517H319.341V117.394H313.222V79.3164H328.391C337.936 79.3164 343.183 84.2144 343.183 92.0749V92.1342C343.183 97.921 340.193 102.029 334.569 103.688L344.114 117.394ZM319.341 84.8662V99.1652H328.391C333.856 99.1652 337.045 96.7952 337.045 92.1144V92.0552C337.045 87.3152 333.837 84.8464 328.391 84.8464H319.341V84.8662Z"/><path d="M356.966 117.394V79.3164H363.085V117.394H356.966Z"/><path d="M406.018 79.3164V85.2019H393.879V117.394H387.7V85.2019H375.561V79.3164H406.018Z"/><path d="M431.445 97.9802L443.208 79.3164H450L434.554 103.471V117.394H428.375V103.471L412.929 79.3164H419.662L431.465 97.9802H431.445Z"/><path d="M114.163 10.5269H107.767C107.213 10.5269 106.777 10.9614 106.777 11.5144V17.1629L72.221 76.966L62.478 58.3417L73.7854 35.9452H78.3401C78.8945 35.9452 79.3302 35.5107 79.3302 34.9577V28.5784C79.3302 28.0254 78.8945 27.5909 78.3401 27.5909H71.9437C71.3893 27.5909 70.9536 28.0254 70.9536 28.5784V30.2966H50.2992V28.5784C50.2992 28.0254 49.8636 27.5909 49.3091 27.5909H42.9128C42.3583 27.5909 41.9226 28.0254 41.9226 28.5784V34.9577C41.9226 35.5107 42.3583 35.9452 42.9128 35.9452H47.4278L59.1511 58.3615L35.7243 104.794L8.3766 52.7327V47.0249C8.3766 46.4719 7.94094 46.0374 7.38646 46.0374H0.990142C0.435663 46.0374 0 46.4719 0 47.0249V53.4042C0 53.9572 0.435663 54.3917 0.990142 54.3917H5.92105L32.4371 104.893C31.9024 104.912 31.4865 105.347 31.4865 105.88V112.259C31.4865 112.812 31.9222 113.247 32.4767 113.247H38.873C39.4275 113.247 39.8631 112.812 39.8631 112.259V105.88C39.8631 105.88 39.8631 105.821 39.8631 105.781C39.8235 105.327 39.4473 104.972 38.972 104.912L60.8343 61.6005L68.8941 77.0055C68.4386 77.0845 68.0624 77.4795 68.0624 77.9535V84.3328C68.0624 84.8858 68.498 85.3203 69.0525 85.3203H75.4489C76.0033 85.3203 76.439 84.8858 76.439 84.3328V77.9535C76.439 77.4597 76.0627 77.0647 75.6073 77.0055L109.193 18.8811H114.163C114.718 18.8811 115.154 18.4466 115.154 17.8936V11.5144C115.154 10.9614 114.718 10.5269 114.163 10.5269ZM60.7947 55.1422L50.2794 35.0367C50.2794 35.0367 50.2794 34.9972 50.2794 34.9774V33.2592H70.9338V34.9774C70.9338 34.9774 70.9338 34.9774 70.9338 34.9972L60.7749 55.1422H60.7947Z"/><path d="M9.28748 40.8627C9.12906 40.8627 8.97063 40.843 8.81221 40.7837C8.39635 40.6455 7.52503 40.3492 7.58443 39.9345C7.64384 39.4605 7.76266 39.263 7.88148 38.9075C15.8422 15.6814 37.1897 1.61938 61.8244 1.61938C76.1815 1.61938 89.291 6.1224 99.9053 15.7407C100.103 15.925 100.348 16.2081 100.638 16.5899C100.876 16.8862 100.262 17.5182 100.004 17.8144C99.4499 18.4267 98.5191 18.4662 97.925 17.9132C87.8652 8.78865 75.4488 4.56214 61.8244 4.56214C38.4571 4.56214 19.684 17.9724 10.6737 39.8752C10.436 40.4677 9.88157 40.8627 9.28748 40.8627Z" fill="#38D92D"/><path d="M26.219 103.944C25.9022 103.865 25.5259 103.609 25.2487 103.391C13.4066 93.6745 6.03995 79.9679 4.53493 64.8197C4.49533 64.4839 4.3369 63.6939 4.61414 63.5359C4.9904 63.3186 5.36665 63.2594 5.84192 63.2199C6.63403 63.1014 7.36674 63.7334 7.46575 64.5432C8.91136 78.9212 15.9018 91.9167 27.13 101.14C27.7637 101.653 27.8231 102.443 27.3082 103.075C27.0112 103.431 26.5161 103.865 26.219 103.984V103.944Z" fill="#38D92D"/><path d="M61.8245 116.446C56.5966 116.446 51.4281 115.755 46.4575 114.372C46.1011 114.274 45.7446 114.214 45.3684 113.977C44.9921 113.74 45.309 112.99 45.4278 112.555C45.6456 111.765 46.4575 111.311 47.2497 111.528C51.9627 112.832 56.8738 113.484 61.8245 113.484C91.9447 113.484 116.441 89.0529 116.441 59.0131C116.441 49.1776 114.262 41.3171 109.233 32.9233C108.817 32.2321 108.916 31.0471 109.708 30.5533C110.104 30.2966 110.322 30.1386 110.678 30.0793C110.975 30.0398 111.431 30.7113 111.609 31.0076C116.896 39.8556 119.391 48.6641 119.391 59.0329C119.391 90.6922 93.5685 116.446 61.8245 116.446Z" fill="#38D92D"/><path d="M35.6254 93.0228L53.1113 58.0653L44.4574 41.3172H38.4968C37.6056 41.3172 36.8927 40.6062 36.8927 39.7175V23.7792C36.8927 22.8904 37.6056 22.1794 38.4968 22.1794H82.7165C83.6077 22.1794 84.3206 22.8904 84.3206 23.7792V39.7372C84.3206 40.626 83.6077 41.337 82.7165 41.337H76.7955L68.4783 57.9665L72.5181 65.7678L97.2914 22.9102C88.1425 13.9832 75.6469 8.4729 61.8443 8.4729C37.467 8.4729 17.1295 25.6357 12.258 48.4865L35.6452 93.0228H35.6254Z" fill="#38D92D"/><path d="M81.8649 76.9266V89.1518C81.8649 90.0406 81.152 90.7516 80.2609 90.7516H64.28C63.3889 90.7516 62.676 90.0406 62.676 89.1518V76.6105L60.8739 73.1148L44.1801 106.473C49.6655 108.507 55.6064 109.613 61.8046 109.613C89.8059 109.613 112.5 86.9793 112.5 59.0528C112.5 50.2245 110.223 41.9295 106.242 34.7207L81.8451 76.9463L81.8649 76.9266Z" fill="#38D92D"/></svg>
          </a>
          <div class="footer-badges">
            <span class="footer-badge"><span class="footer-badge-dot"></span>SOC2 Type II Certified</span>
            <span class="footer-badge"><span class="footer-badge-dot"></span>Black Hat USA 2024 Finalist</span>
            <span class="footer-badge"><span class="footer-badge-dot"></span>G2 High Performer - SAST Spring 2026</span>
          </div>
          <a href="https://www.g2.com/products/dryrun-security/reviews" target="_blank" rel="noopener noreferrer" class="footer-g2-link">Read our reviews on G2</a>
        </div>
        <div class="footer-col">
          <p class="footer-col-title">Links</p>
          <ul class="footer-links">
            <li><a href="https://www.dryrun.security/blog" target="_blank" rel="noopener noreferrer">Blog</a></li>
            <li><a href="https://www.dryrun.security/faqs" target="_blank" rel="noopener noreferrer">FAQ</a></li>
            <li><a href="https://www.dryrun.security/brand-guidelines" target="_blank" rel="noopener noreferrer">Brand Guidelines</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <p class="footer-col-title">Product</p>
          <ul class="footer-links">
            <li><a href="https://www.dryrun.security/product/sast" target="_blank" rel="noopener noreferrer">SAST</a></li>
            <li><a href="https://www.dryrun.security/product/pr-code-reviews" target="_blank" rel="noopener noreferrer">PR Code Reviews</a></li>
            <li><a href="https://www.dryrun.security/product/sast-deepscan-full-repository-security-scan" target="_blank" rel="noopener noreferrer">Repository Reviews</a></li>
            <li><a href="https://www.dryrun.security/product/custom-code-policies" target="_blank" rel="noopener noreferrer">Custom Code Policies</a></li>
            <li><a href="https://www.dryrun.security/product/codebase-intelligence" target="_blank" rel="noopener noreferrer">Codebase Intelligence</a></li>
            <li><a href="https://www.dryrun.security/product/application-security-secrets" target="_blank" rel="noopener noreferrer">Secrets</a></li>
            <li><a href="https://www.dryrun.security/product/infrastructure-as-code-iac-security" target="_blank" rel="noopener noreferrer">Infrastructure as Code</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <p class="footer-col-title">Social</p>
          <ul class="footer-social-links">
            <li>
              <a href="https://www.linkedin.com/company/dryrun-security/" target="_blank" rel="noopener noreferrer">
                <svg class="footer-social-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                LinkedIn
              </a>
            </li>
            <li>
              <a href="https://x.com/DryRunSec" target="_blank" rel="noopener noreferrer">
                <svg class="footer-social-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.74l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                X (Twitter)
              </a>
            </li>
            <li>
              <a href="mailto:hello@dryrun.security">
                <svg class="footer-social-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                hello@dryrun.security
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-bottom-inner">
        <p class="footer-copy">&copy; 2026 DryRun Security. All rights reserved.</p>
        <nav class="footer-legal">
          <a href="https://www.dryrun.security/privacy-policy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
          <span class="footer-legal-sep">|</span>
          <a href="https://www.dryrun.security/terms-of-service" target="_blank" rel="noopener noreferrer">Terms of Service</a>
          <span class="footer-legal-sep">|</span>
          <a href="https://www.dryrun.security/code-safety" target="_blank" rel="noopener noreferrer">Code Safety</a>
        </nav>
      </div>
    </div>
  </footer>'''


def render_doc_page(slug: str, page: dict, asset_prefix: str = '../',
                    search_index: str = '[]') -> str:
    title = page['title']
    description = page['description']
    section_name = page.get('section', get_section_for_slug(slug))
    raw_content = page['content'].strip()
    raw_content = raw_content.replace('{asset_prefix}', asset_prefix)
    content_with_ids = inject_heading_ids(raw_content)
    toc_items = extract_toc(content_with_ids)

    header = HEADER_HTML.replace('{asset_prefix}', asset_prefix)
    footer = FOOTER_HTML.replace('{asset_prefix}', asset_prefix)
    sidebar = render_sidebar(slug, asset_prefix)
    toc = render_toc(toc_items)
    prev_next = render_prev_next(slug, asset_prefix)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} - DryRun Security Docs</title>
  <meta name="description" content="{esc(description)}">
  <link rel="icon" href="{asset_prefix}assets/favicon.ico" type="image/png">
  <link rel="apple-touch-icon" href="{asset_prefix}assets/logo192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{asset_prefix}style.css">
</head>
<body>
{header}
  <div class="docs-layout">
{sidebar}
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="document.querySelector('.sidebar').classList.remove('open');document.getElementById('sidebarOverlay').style.display='none'"></div>
    <main class="content-area">
      <div class="content-inner">
        <div class="breadcrumb"><a href="{asset_prefix}index.html">Docs</a><span class="breadcrumb-sep">\u203a</span>{esc(section_name)}</div>
        <div class="page-heading-row">
          <h1 class="page-heading">{esc(title)}</h1>
          <button class="btn-download-pdf" onclick="window.print()" title="Download as PDF"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2v8M4.5 7.5 8 10l3.5-2.5"/><path d="M2.5 11v2a1 1 0 001 1h9a1 1 0 001-1v-2"/></svg><span>PDF</span></button>
        </div>
        <p class="page-description">{esc(description)}</p>
        <div class="doc-content">
{content_with_ids}
        </div>
{prev_next}
      </div>
    </main>
{toc}
  </div>
{footer}
  <script>window.__SEARCH_INDEX__={search_index};</script>
  <script src="{asset_prefix}app.js"></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Index page - renders the documentation intro in doc-page layout
# ---------------------------------------------------------------------------

def render_index_page() -> str:
    """Render index.html as a landing page with hero, persona cards, and feature grid."""
    asset_prefix = './'
    description = 'DryRun Security documentation - AI-native application security for your development workflow.'

    header = HEADER_HTML.replace('{asset_prefix}', asset_prefix)
    footer = FOOTER_HTML.replace('{asset_prefix}', asset_prefix)
    sidebar = render_sidebar('documentation', asset_prefix)
    search_index = generate_search_index()

    dp = './docs/'

    landing_content = f'''
        <h1 class="page-heading">Documentation</h1>
        <p class="page-description">DryRun Security is an AI-native application security platform that reviews every pull request for vulnerabilities in real time. These docs cover setup, scanning configuration, code security intelligence, platform administration, and integrations.</p>
        <div class="doc-content">
        <div class="landing-hero"></div>

        <div class="landing-section">
          <div class="landing-section-header">
            <h2>Get Started</h2>
          </div>
          <div class="landing-grid cols-3">
            <a class="landing-card persona" href="{esc(dp)}quick-start.html">
              <span class="landing-card-title">I&#x27;m a Developer</span>
              <span class="landing-card-desc">Connect your repo, enable PR scanning, and get security findings inline with your pull requests.</span>
            </a>
            <a class="landing-card persona" href="{esc(dp)}deepscan.html">
              <span class="landing-card-title">I&#x27;m in AppSec</span>
              <span class="landing-card-desc">Discover vulnerabilities across repositories, review findings, configure policies, and track compliance.</span>
            </a>
            <a class="landing-card persona" href="{esc(dp)}pr-scanning-configuration.html">
              <span class="landing-card-title">I&#x27;m an Admin</span>
              <span class="landing-card-desc">Set up integrations, manage team permissions, configure scanning settings, and generate API tokens.</span>
            </a>
          </div>
        </div>

        <div class="landing-section">
          <div class="landing-section-header">
            <h2>Scanning Products</h2>
          </div>
          <div class="landing-grid cols-3">
            <a class="landing-card" href="{esc(dp)}pr-scanning.html">
              <span class="landing-card-title">PR Scanning</span>
              <span class="landing-card-desc">Automatic security review on every pull request with contextual analysis and inline comments.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}deepscan.html">
              <span class="landing-card-title">Repository Scanning (DeepScan)</span>
              <span class="landing-card-desc">Full repository analysis for comprehensive vulnerability detection beyond individual PRs.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}secrets-scanning.html">
              <span class="landing-card-title">Secrets Scanning</span>
              <span class="landing-card-desc">Detect leaked credentials, API keys, and tokens before they reach production.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}iac-scanning.html">
              <span class="landing-card-title">IaC Scanning</span>
              <span class="landing-card-desc">Security analysis for Terraform, CloudFormation, and other infrastructure-as-code configurations.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}sca.html">
              <span class="landing-card-title">SCA</span>
              <span class="landing-card-desc">Software composition analysis for known vulnerabilities in open-source dependencies.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}auto-fix.html">
              <span class="landing-card-title">Auto Fix</span>
              <span class="landing-card-desc">Automated remediation suggestions with one-click fix verification.</span>
            </a>
          </div>
        </div>

        <div class="landing-section">
          <div class="landing-section-header">
            <h2>Code Security Intelligence</h2>
          </div>
          <div class="landing-grid cols-3">
            <a class="landing-card" href="{esc(dp)}vulnerability-trends.html">
              <span class="landing-card-title">Vulnerability Trends</span>
              <span class="landing-card-desc">Track vulnerability coverage and risk trends over time across your organization.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}architecture-risks.html">
              <span class="landing-card-title">Architecture Risks</span>
              <span class="landing-card-desc">Identify structural security risks and systemic patterns across your codebase.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}developer-trends.html">
              <span class="landing-card-title">Developer Trends</span>
              <span class="landing-card-desc">Analyze developer behavior patterns and security trend data.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}shadow-ai.html">
              <span class="landing-card-title">Shadow AI</span>
              <span class="landing-card-desc">Detect and govern unauthorized AI tool usage in your codebase.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}incident-response.html">
              <span class="landing-card-title">Incident Response</span>
              <span class="landing-card-desc">Investigate security incidents with queryable code intelligence.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}application-summary.html">
              <span class="landing-card-title">Application Summary</span>
              <span class="landing-card-desc">Dashboard overview of your application security posture.</span>
            </a>
          </div>
        </div>

        <div class="landing-section">
          <div class="landing-section-header">
            <h2>Platform &amp; Integrations</h2>
          </div>
          <div class="landing-grid cols-3">
            <a class="landing-card" href="{esc(dp)}pr-blocking.html">
              <span class="landing-card-title">PR Blocking</span>
              <span class="landing-card-desc">Block pull requests based on security finding severity and policy rules.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}custom-code-policies.html">
              <span class="landing-card-title">Custom Code Policies</span>
              <span class="landing-card-desc">Create custom security rules in plain English to enforce your standards.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}compliance-grc.html">
              <span class="landing-card-title">Compliance &amp; GRC</span>
              <span class="landing-card-desc">Compliance reporting, audit trails, and governance readiness.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}slack-integration.html">
              <span class="landing-card-title">Slack Integration</span>
              <span class="landing-card-desc">Receive real-time security alerts and findings in your Slack channels.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}webhook-integration.html">
              <span class="landing-card-title">Webhook Integration</span>
              <span class="landing-card-desc">Send DryRun Security events to any webhook endpoint for custom workflows.</span>
            </a>
            <a class="landing-card" href="{esc(dp)}mcp.html">
              <span class="landing-card-title">MCP</span>
              <span class="landing-card-desc">Model Context Protocol integration for AI-powered development tools.</span>
            </a>
          </div>
        </div>

        <div class="landing-section">
          <div class="landing-section-header">
            <h2>Resources</h2>
          </div>
          <div class="landing-resources">
            <a href="{esc(dp)}documentation.html">
              <span>Documentation Overview<span class="res-desc">Full table of contents and platform overview</span></span>
            </a>
            <a href="{esc(dp)}dryrun-api.html">
              <span>DryRun API<span class="res-desc">Programmatic access to DryRun Security</span></span>
            </a>
            <a href="{esc(dp)}api-access-keys.html">
              <span>API Access Keys<span class="res-desc">Manage API keys for integrations</span></span>
            </a>
            <a href="{esc(dp)}ai-coding-integration.html">
              <span>AI Coding Integration<span class="res-desc">Integrate with AI coding tools and agents</span></span>
            </a>
          </div>
        </div>
        </div>
'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DryRun Security Documentation</title>
  <meta name="description" content="{esc(description)}">
  <link rel="icon" href="{asset_prefix}assets/favicon.ico" type="image/png">
  <link rel="apple-touch-icon" href="{asset_prefix}assets/logo192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{asset_prefix}style.css">
</head>
<body>
{header}
  <div class="docs-layout">
{sidebar}
    <div class="sidebar-overlay" id="sidebarOverlay" onclick="document.querySelector('.sidebar').classList.remove('open');document.getElementById('sidebarOverlay').style.display='none'"></div>
    <main class="content-area">
      <div class="content-inner">
{landing_content}
      </div>
    </main>
  </div>
{footer}
  <script>window.__SEARCH_INDEX__={search_index};</script>
  <script src="{asset_prefix}app.js"></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Sitemap and robots.txt
# ---------------------------------------------------------------------------

def render_sitemap(base_url: str = 'https://docs.dryrun.security') -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    lines.append(f'  <url><loc>{base_url}/</loc><priority>1.0</priority></url>')
    for slug in ORDERED_PAGES:
        lines.append(f'  <url><loc>{base_url}/docs/{slug}.html</loc><priority>0.8</priority></url>')
    lines.append('</urlset>')
    return '\n'.join(lines)


def render_robots() -> str:
    return '''User-agent: *
Allow: /

Sitemap: https://docs.dryrun.security/sitemap.xml
'''


# ---------------------------------------------------------------------------
# Search index generation
# ---------------------------------------------------------------------------

_TAG_RE = re.compile(r'<[^>]+>')
_WHITESPACE_RE = re.compile(r'\s+')


def _strip_html(raw_html: str) -> str:
    """Remove HTML tags and collapse whitespace to produce plain text."""
    text = _TAG_RE.sub(' ', raw_html)
    text = html.unescape(text)
    text = _WHITESPACE_RE.sub(' ', text).strip()
    return text


_HEADING_SPLIT_RE = re.compile(
    r'(<h[23][^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</h[23]>)',
    re.IGNORECASE | re.DOTALL,
)


def _extract_sections(content_html: str):
    """Split HTML content into sections delimited by h2/h3 headings.

    Returns a list of (anchor, heading_text, section_body_html) tuples.
    """
    matches = list(_HEADING_SPLIT_RE.finditer(content_html))
    if not matches:
        return []
    sections = []
    for i, m in enumerate(matches):
        anchor = m.group(2)
        heading_text = html.unescape(re.sub(r'<[^>]+>', '', m.group(3)).strip())
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content_html)
        body_html = content_html[start:end]
        sections.append((anchor, heading_text, body_html))
    return sections


def generate_search_index() -> str:
    """Build a JSON search index of all pages with section-level entries.

    Each page gets a page-level entry (no anchor) plus one entry per h2/h3
    section that includes the anchor id for deep linking.
    """
    index = []
    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            continue
        content_html = page.get('content', '')
        content_with_ids = inject_heading_ids(content_html)
        plain_text = _strip_html(content_html)
        # Page-level entry (no anchor)
        index.append({
            's': slug,
            't': page.get('title', slug),
            'n': page.get('section', ''),
            'd': page.get('description', ''),
            'b': plain_text,
        })
        # Section-level entries with anchors
        for anchor, heading, body_html in _extract_sections(content_with_ids):
            section_text = _strip_html(body_html)
            if len(section_text.strip()) < 20:
                continue
            index.append({
                's': slug,
                't': heading,
                'n': page.get('section', ''),
                'd': '',
                'b': section_text,
                'a': anchor,
            })
    return json.dumps(index, separators=(',', ':'))


# ---------------------------------------------------------------------------
# Webflow export
# ---------------------------------------------------------------------------

_INLINE_STYLE_RE = re.compile(r'\s+style="[^"]*"', re.IGNORECASE)
_SCRIPT_TAG_RE = re.compile(
    r'<script[\s>].*?</script>', re.IGNORECASE | re.DOTALL
)
_CLASS_ATTR_RE = re.compile(r'class="([^"]*)"')
_ASSET_PREFIX_RE = re.compile(r'\{asset_prefix\}')

# CSS class names used in page content that need the drs- prefix
_DRS_CLASS_MAP = {
    'landing-hero': 'drs-landing-hero',
    'landing-section': 'drs-landing-section',
    'landing-section-header': 'drs-landing-section-header',
    'landing-grid': 'drs-landing-grid',
    'landing-card': 'drs-landing-card',
    'landing-card-title': 'drs-landing-card-title',
    'landing-card-desc': 'drs-landing-card-desc',
    'landing-resources': 'drs-landing-resources',
    'res-desc': 'drs-res-desc',
    'cols-2': 'drs-cols-2',
    'cols-3': 'drs-cols-3',
    'persona': 'drs-persona',
    'doc-content': 'drs-doc-content',
    'info-box': 'drs-info-box',
    'warning-box': 'drs-warning-box',
    'feature-grid': 'drs-feature-grid',
    'feature-item': 'drs-feature-item',
    'feature-icon': 'drs-feature-icon',
    'code-block': 'drs-code-block',
    'copy-btn': 'drs-copy-btn',
}


def _clean_content_for_webflow(raw_content: str) -> str:
    """Clean page content HTML for Webflow compatibility.

    - Removes inline styles
    - Removes <script> tags
    - Remaps CSS class names to drs- prefixed versions
    - Removes {asset_prefix} placeholders (replaces with relative paths)
    """
    content = raw_content.strip()

    # Remove {asset_prefix} references - use relative paths for Webflow
    content = _ASSET_PREFIX_RE.sub('', content)

    # Remove inline styles
    content = _INLINE_STYLE_RE.sub('', content)

    # Remove script tags
    content = _SCRIPT_TAG_RE.sub('', content)

    # Remap class names to drs- prefix
    def _remap_classes(m):
        original = m.group(1)
        classes = original.split()
        remapped = []
        for cls in classes:
            remapped.append(_DRS_CLASS_MAP.get(cls, cls))
        return f'class="{" ".join(remapped)}"'

    content = _CLASS_ATTR_RE.sub(_remap_classes, content)

    # Inject heading IDs for proper anchor linking
    content = inject_heading_ids(content)

    return content


def _extract_meta_description(content: str) -> str:
    """Extract a meta description from the first <p> tag in the content."""
    match = re.search(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
    if not match:
        return ''
    text = _strip_html(match.group(1)).strip()
    if len(text) > 160:
        text = text[:157] + '...'
    return text


def generate_webflow_csv(output_dir: Path) -> None:
    """Generate a CSV file for Webflow CMS import with all documentation pages."""
    webflow_dir = output_dir / 'webflow-export'
    webflow_dir.mkdir(parents=True, exist_ok=True)

    csv_path = webflow_dir / 'pages.csv'
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['Name', 'Slug', 'Content', 'Meta Description', 'Category'])

    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            continue
        title = page['title']
        description = page.get('description', '')
        section = page.get('section', get_section_for_slug(slug))
        raw_content = page['content']
        clean = _clean_content_for_webflow(raw_content)

        meta_desc = description if description else _extract_meta_description(clean)

        writer.writerow([title, slug, clean, meta_desc, section])

    csv_path.write_text(buf.getvalue(), encoding='utf-8')
    print(f'  Generated: webflow-export/pages.csv')


def generate_webflow_pages(output_dir: Path) -> None:
    """Generate individual clean HTML content files for Webflow code embeds."""
    pages_dir = output_dir / 'webflow-export' / 'pages'
    pages_dir.mkdir(parents=True, exist_ok=True)

    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            continue
        raw_content = page['content']
        clean = _clean_content_for_webflow(raw_content)

        page_html = f'<div class="drs-doc-content">\n{clean}\n</div>\n'
        out_path = pages_dir / f'{slug}.html'
        out_path.write_text(page_html, encoding='utf-8')

    print(f'  Generated: webflow-export/pages/ ({len(ORDERED_PAGES)} files)')


def generate_webflow_readme(output_dir: Path) -> None:
    """Generate a README explaining how to use the Webflow export files."""
    webflow_dir = output_dir / 'webflow-export'
    webflow_dir.mkdir(parents=True, exist_ok=True)

    # Collect all drs- classes actually used across content
    all_classes = set()
    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            continue
        clean = _clean_content_for_webflow(page['content'])
        for m in _CLASS_ATTR_RE.finditer(clean):
            for cls in m.group(1).split():
                if cls.startswith('drs-'):
                    all_classes.add(cls)

    class_table = '\n'.join(
        f'| `{cls}` | {cls.replace("drs-", "").replace("-", " ").title()} container/element |'
        for cls in sorted(all_classes)
    )

    readme = f'''# Webflow Export - DryRun Security Documentation

This directory contains DryRun Security documentation content formatted for
import into Webflow.

## Files

- **pages.csv** - All documentation pages in CSV format for Webflow CMS import
- **pages/*.html** - Individual HTML content files for use as Webflow Code Embeds
- **README.md** - This file

## Using the CSV for CMS Import

1. In Webflow, go to **CMS** > **Import/Export** (or use the API).
2. Upload `pages.csv`.
3. Map the columns to your CMS Collection fields:
   - `Name` -> Page title (plain text field)
   - `Slug` -> URL slug (slug field)
   - `Content` -> Page body (Rich Text or plain HTML field for Code Embed)
   - `Meta Description` -> SEO description (plain text field)
   - `Category` -> Section grouping (option/reference field)
4. Content is clean HTML suitable for Webflow Rich Text fields. If your Rich
   Text field strips custom classes, use a Code Embed element instead.

## Using Individual HTML Files as Code Embeds

Each file in `pages/` contains only the page body content wrapped in a single
`<div class="drs-doc-content">` element. To use in Webflow:

1. Add a **Code Embed** element to your page template.
2. Paste the contents of the corresponding `.html` file.
3. The HTML uses semantic tags (`h2`, `h3`, `h4`, `p`, `ul`, `ol`, `li`,
   `table`, `thead`, `tbody`, `tr`, `th`, `td`, `pre`, `code`, `strong`, `em`,
   `a`) that Webflow styles natively.
4. Custom layout classes use the `drs-` prefix to avoid conflicts with
   Webflow\'s own class namespace.

## CSS Classes

All custom CSS classes use the `drs-` prefix. Add these styles to your
Webflow project\'s custom CSS (Site Settings > Custom Code > Head):

| Class | Purpose |
|-------|---------|
{class_table}

Copy the relevant styles from the original `style.css` file, renaming each
class to its `drs-` prefixed version. Semantic HTML elements (`h2`, `p`,
`table`, etc.) inherit Webflow\'s typography styles by default.

## Images and Assets

Images referenced in the content use relative paths. Before importing:

1. Upload all images from the `assets/` directory to Webflow\'s Asset Manager.
2. Update image `src` attributes in the HTML to point to Webflow-hosted URLs,
   or use Webflow\'s built-in image elements and reference CMS image fields.
3. SVG logos are inlined in the original site\'s header/footer and are **not**
   included in these content files. Use Webflow\'s native header/footer
   components instead.

## Notes

- Content HTML has been cleaned: no inline styles, no `<script>` tags, and
  no site wrapper elements (header, footer, sidebar, navigation).
- Internal links between pages use relative paths (e.g., `deepscan.html`).
  Update these to match your Webflow URL structure if slugs differ.
- Tables use standard HTML table markup (`<table>`, `<thead>`, `<tbody>`,
  `<tr>`, `<th>`, `<td>`) compatible with Webflow\'s table styling.
'''

    (webflow_dir / 'README.md').write_text(readme, encoding='utf-8')
    print(f'  Generated: webflow-export/README.md')


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------

def build(output_dir: str = None) -> None:
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)

    docs_dir = output_dir / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Pre-generate the search index once for all pages
    search_index = generate_search_index()

    # Generate doc pages
    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            print(f'WARNING: No content defined for slug: {slug}')
            continue
        html_content = render_doc_page(slug, page, asset_prefix='../',
                                       search_index=search_index)
        out_path = docs_dir / f'{slug}.html'
        out_path.write_text(html_content, encoding='utf-8')
        print(f'  Generated: docs/{slug}.html')

    # Generate index
    index_html = render_index_page()
    (output_dir / 'index.html').write_text(index_html, encoding='utf-8')
    print('  Generated: index.html')

    # Sitemap
    (output_dir / 'sitemap.xml').write_text(render_sitemap(), encoding='utf-8')
    print('  Generated: sitemap.xml')

    # Robots
    (output_dir / 'robots.txt').write_text(render_robots(), encoding='utf-8')
    print('  Generated: robots.txt')

    # Webflow export
    generate_webflow_csv(output_dir)
    generate_webflow_pages(output_dir)
    generate_webflow_readme(output_dir)

    total = len(ORDERED_PAGES) + 3  # pages + index + sitemap + robots
    webflow_total = len(ORDERED_PAGES) + 2  # pages + CSV + README
    print(f'\nBuild complete: {total} site files + {webflow_total} webflow-export files generated in {output_dir}')


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else None
    build(out)
