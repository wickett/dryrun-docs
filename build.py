"""
DryRun Security Documentation Site Generator
Generates all HTML pages for the docs site.
Usage: python3 build.py
"""
import html
import os
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
        'pages': ['quick-start', 'quick-start-gitlab'],
    },
    {
        'name': 'Scanning',
        'slug': 'scanning',
        'pages': [
            'sast-overview', 'pr-code-reviews', 'deepscan',
            'secrets-detection', 'sca', 'iac-scanning', 'coverage-matrix',
        ],
    },
    {
        'name': 'AI & Intelligence',
        'slug': 'ai-intelligence',
        'pages': [
            'ai-native-architecture', 'contextual-security-analysis',
            'business-logic-detection', 'git-behavioral-analysis',
            'code-security-knowledge-graph', 'natural-language-code-policies',
            'nlcp-starter-pack', 'nlcp-best-practices',
        ],
    },
    {
        'name': 'Remediation',
        'slug': 'remediation',
        'pages': ['auto-fix', 'fix-verification', 'finding-dismissal'],
    },
    {
        'name': 'Platform',
        'slug': 'platform',
        'pages': [
            'risk-register', 'security-dashboard', 'configurations',
            'notifications', 'ai-insights', 'risk-trending', 'sbom-generation',
        ],
    },
    {
        'name': 'Developer Tools',
        'slug': 'developer-tools',
        'pages': ['ide-integration', 'mcp-integration', 'agents-md', 'cicd-integration'],
    },
    {
        'name': 'AI Agent Security',
        'slug': 'ai-agent-security',
        'pages': ['securing-ai-code', 'malicious-agent-detection', 'ai-coding-visibility'],
    },
    {
        'name': 'API Reference',
        'slug': 'api-reference',
        'pages': ['api-guide', 'language-support'],
    },
]


# ---------------------------------------------------------------------------
# Page content definitions
# ---------------------------------------------------------------------------

PAGES = {}


# -- Getting Started --

PAGES['quick-start'] = {
    'title': 'Install DryRun Security',
    'description': 'Install the DryRun Security GitHub App and start scanning pull requests in minutes.',
    'section': 'Getting Started',
    'content': '''
<h2 id="authorize-and-install">Authorize and Install the DryRun Security GitHub Application</h2>

<ol>
  <li>
    <p>Navigate to <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a> and click the <strong>Log in with GitHub</strong> button.</p>
  </li>
  <li>
    <p>Log in to the GitHub account where DryRun Security will be installed.</p>
  </li>
  <li>
    <p>Authorize the DryRun Security GitHub Application by clicking the <strong>Authorize DryRunSecurity</strong> button.</p>
    <p><strong>Note:</strong> This is a standard authorization screen for all applications in GitHub.</p>
  </li>
  <li>
    <p>You'll be redirected to the DryRun Security portal. Click the <strong>Install</strong> button.</p>
  </li>
  <li>
    <p>Click the <strong>Install</strong> button on the DryRunSecurity GitHub Application page.</p>
  </li>
  <li>
    <p>Choose the GitHub repositories DryRun Security will run by selecting <strong>All Repositories</strong> or <strong>Only selected repositories</strong>.</p>
  </li>
  <li>
    <p>After step one your installation may be paused for up to 2 business days as we activate your account.</p>
  </li>
  <li>
    <p>Once your account has been activated, you'll see the <strong>Installation Complete</strong> message the next time you visit <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</p>
  </li>
</ol>

<p><strong>Congratulations!</strong> Installation is complete. At this point DryRun Security will run checks on your repository as code is committed to Pull Requests.</p>

<h2 id="whats-next">What's Next</h2>

<p>Now that DryRun Security is installed, open a Pull Request against one of your selected repositories. DryRun Security will automatically run its security analysis and post results as a PR comment and in the GitHub Checks area.</p>

<ul>
  <li>See <a href="./pr-code-reviews.html">PR Code Reviews</a> to understand how DryRun Security analyzes your pull requests.</li>
  <li>See <a href="./configurations.html">Configurations</a> to customize which agents and policies run on each repository.</li>
  <li>See <a href="./natural-language-code-policies.html">Natural Language Code Policies</a> to create custom security rules in plain English.</li>
</ul>
''',
}

PAGES['quick-start-gitlab'] = {
    'title': 'Install DryRun Security for GitLab',
    'description': 'Connect DryRun Security to your GitLab environment for contextual code review on Merge Requests.',
    'section': 'Getting Started',
    'content': '''
<p>DryRun Security for GitLab.com enables fast, contextual code reviews that help your team spot unknown risks before they start. This guide walks you through connecting your GitLab environment to DryRun Security by creating a Personal Access Token and completing the installation in the dashboard.</p>

<h2 id="create-a-personal-access-token">Create a Personal Access Token</h2>

<p>This section describes creating a Personal Access Token (PAT) that will be used during the installation of DryRun Security.</p>

<p><strong>Note:</strong> The GitLab user used to create the PAT needs to have at least <code>Maintainer</code> access to the Group or Project where DryRun Security will run.</p>

<h3 id="generating-the-pat">Generating the Personal Access Token</h3>

<ol>
  <li>Log in to <a href="https://gitlab.com" target="_blank" rel="noopener noreferrer">gitlab.com</a>.</li>
  <li>Navigate to <a href="https://gitlab.com/-/user_settings/personal_access_tokens" target="_blank" rel="noopener noreferrer">https://gitlab.com/-/user_settings/personal_access_tokens</a>.</li>
  <li>Under <strong>Personal Access Tokens</strong> click <strong>Add new token</strong>.</li>
  <li>Add a token name and select the <code>api</code> and <code>read_user</code> scopes.</li>
  <li>Click <strong>Create personal access token</strong>.</li>
  <li>Copy the token and <strong>save it for later use</strong> - it will not be shown again.</li>
  <li>Verify that the user who created the PAT has access to the <strong>Group</strong> where DryRun Security will be installed. The user should have at least <strong>Maintainer</strong> access. Add the user if necessary.</li>
</ol>

<h2 id="install-via-dashboard">Install DryRun Security via the Dashboard</h2>

<ol>
  <li>Navigate to <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a> and click the <strong>Log in with GitLab</strong> button.</li>
  <li>Authorize the DryRun Security OAuth Application.
    <br><strong>Important:</strong> Choose the User or Group where DryRun Security will run from the User/Group Selector. This is usually a GitLab Group.</li>
  <li>Click the <strong>Add Token</strong> button or navigate to <strong>Settings &gt; GitLab</strong>.</li>
  <li>Enter the Personal Access Token created earlier and click <strong>Save Token</strong>.</li>
  <li>Verify the User/Group for the Installation and click <strong>Confirm</strong> to confirm API access.</li>
  <li>Install on projects by clicking <strong>+</strong> next to the project and then click <strong>Save Projects</strong>.</li>
</ol>

<h2 id="activation">Activation</h2>

<p>Your installation may be paused for up to 2 business days as we activate your account. We'll notify you by email once your account is active.</p>

<p>Once your account has been activated, you'll see the <strong>Installation Complete</strong> message the next time you visit <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</p>

<p><strong>Congratulations!</strong> Installation is complete. DryRun Security will now run and analyze changes as code is committed to Merge Requests.</p>
''',
}


# -- Scanning --

PAGES['sast-overview'] = {
    'title': 'How DryRun Security SAST Works',
    'description': "An overview of DryRun Security's Contextual Security Analysis - an AI-native approach to static analysis that evaluates code in full context, not by pattern matching.",
    'section': 'Scanning',
    'content': '''
<h2 id="not-pattern-matching">This Is Not Pattern Matching</h2>

<p>Traditional static application security testing (SAST) tools work by comparing your code against a database of known-bad patterns. If a function call or code fragment matches a signature, it gets flagged. This approach is fast to implement and easy to explain - but it misses the vast majority of real vulnerabilities while generating enormous volumes of noise on code that happens to look like a pattern but is actually safe.</p>

<p>DryRun Security takes a fundamentally different approach. Our <strong>Contextual Security Analysis (CSA)</strong> evaluates code within its full context: the data flowing into a function, the authorization logic surrounding it, the framework being used, the developer's apparent intent, and the broader architecture of the application. A SQL query constructed from user input is only a problem if input sanitization is absent - and CSA can determine that, while a pattern matcher cannot.</p>

<h2 id="how-csa-works">How Contextual Security Analysis Works</h2>

<p>When a Pull Request is opened, DryRun Security's Code Review Agent retrieves the diff along with the relevant surrounding code context. It does not analyze the diff in isolation - it considers the complete code path, imported libraries, authentication middleware, and any applicable security policies configured for the repository.</p>

<p>The analysis is performed by a multi-agent system where each specialized agent focuses on a specific class of vulnerability or security concern. The SQL Injection Analyzer, for example, traces the full data flow from input to query execution. The Secrets Analyzer looks for credential patterns in context - distinguishing between a real API key and a test fixture. Each agent reports findings with precise file locations and a plain-language explanation of the risk.</p>

<h2 id="ai-native-architecture">AI-Native Architecture</h2>

<p>DryRun Security is built AI-first. Every layer of the platform - from ingestion to analysis to reporting - is designed around large language model capabilities rather than bolted on top of a legacy rules engine. This means findings reflect the same kind of reasoning a senior security engineer would apply: considering intent, context, and consequence rather than matching syntax.</p>

<p>Importantly, DryRun uses <strong>model-independent verification</strong>. Findings are validated across multiple AI models before being surfaced, reducing hallucinations and ensuring that every result has been cross-checked. This multi-model approach means DryRun Security is not dependent on the behavior of any single model provider, and findings remain consistent even as underlying models evolve.</p>

<h2 id="what-this-means-for-developers">What This Means for Developers</h2>

<p>The practical impact of contextual analysis is dramatically lower false-positive rates. Developers spend less time dismissing irrelevant alerts and more time addressing findings that represent genuine risk. Because findings include full context - the affected code path, the reason the vulnerability exists, and suggested remediation - they are immediately actionable without requiring a security expert to interpret them.</p>

<p>DryRun Security integrates directly into the Pull Request workflow on GitHub and GitLab, so developers receive security feedback in the same place they already work. No separate dashboard to check, no end-of-sprint security reviews - security analysis happens in real time as code is being written.</p>

<h2 id="coverage">Coverage</h2>

<p>DryRun Security's agents cover over 47 vulnerability categories, from SQL injection and cross-site scripting to business logic flaws, IDOR, and AI-specific risks like prompt injection. See the <a href="./coverage-matrix.html">Coverage Matrix</a> for the full list with CWE mappings.</p>
''',
}

PAGES['pr-code-reviews'] = {
    'title': 'PR Code Reviews',
    'description': 'How DryRun Security analyzes pull requests and surfaces findings in GitHub and GitLab.',
    'section': 'Scanning',
    'content': '''
<p>In this section we describe how DryRun Security runs and where to see the results. To illustrate, we walk through an example of modifying code in a sample repository and reviewing the results.</p>

<h2 id="open-a-pull-request">Open a Pull Request</h2>

<p>When code is updated and a Pull Request is opened, DryRun Security's Policy Enforcement Agent will immediately run any user-configured Natural Language Code Policies against the code. DryRun Security's many Code Security Agents will also run against the code and report back with any findings.</p>

<p>You'll see the results of the analysis in both a summary comment and the Checks area of the Pull Request.</p>

<h2 id="dryrun-security-summary">DryRun Security Summary</h2>

<p>DryRun Security generates a summary describing the security implications of the change. If any Code Policies or Code Security Agents have findings, they will be described in this summary.</p>

<h2 id="policy-enforcement">Policy Enforcement</h2>

<p>The Policy Enforcement Agent runs any user-configured Natural Language Code Policies that are set up for the repository. If a policy has findings, they will be listed in the Pull Request comment. This enables your team to enforce custom, organization-specific security rules - like "no new API endpoints without authorization" - written in plain English.</p>

<h2 id="code-security">Code Security</h2>

<p>The summary also lists any findings from DryRun Security's Code Security Agents. Each agent is specialized for a specific class of vulnerability - SQL injection, secrets exposure, IDOR, insecure dependencies, and more. Click on a finding to see more details about the affected code path and recommended fix.</p>

<h2 id="risk-level">Risk Level</h2>

<p>DryRun Security calculates and assigns a risk level to each change: <strong>Critical</strong>, <strong>High</strong>, <strong>Medium</strong>, or <strong>Low</strong>. This risk level can be used to trigger notifications or block the merging of a Pull Request via GitHub Branch Protection Rules.</p>

<h2 id="github-checks">GitHub Checks</h2>

<p>DryRun Security also posts agent results to the <strong>Checks</strong> area on the Pull Request. This can be seen on the Pull Request default page or by clicking the <strong>Checks</strong> tab at the top of the Pull Request page.</p>

<p>Each check corresponds to a specific agent or policy. Click on a check to see its details. Expand a finding's dropdown to view the finding type, description, file name, and a direct link to the code where the finding was detected.</p>

<h2 id="gitlab-merge-requests">GitLab Merge Requests</h2>

<p>DryRun Security works identically on GitLab, posting findings as Merge Request comments and in the GitLab pipeline status checks area. See <a href="../quick-start-gitlab.html">Install DryRun Security for GitLab</a> for setup instructions.</p>
''',
}

PAGES['deepscan'] = {
    'title': 'DeepScan - Full Repository Scan',
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

<h2 id="how-deepscan-differs-from-pr-reviews">How DeepScan Differs from PR Reviews</h2>

<p>PR Code Reviews operate on the diff - the lines added or changed in a specific pull request. DeepScan operates on the entire tree of the repository at a given commit. This means DeepScan can:</p>

<ul>
  <li>Trace multi-file data flows that span across modules and services</li>
  <li>Identify patterns that only become apparent when viewing the full codebase together</li>
  <li>Find vulnerabilities in code that predates DryRun Security's installation</li>
  <li>Discover nested <code>AGENTS.md</code> security guidelines and apply them across the full analysis</li>
</ul>

<h2 id="deepscan-findings-in-the-risk-register">DeepScan Findings in the Risk Register</h2>

<p>DeepScan results appear alongside PR findings in the <a href="../risk-register.html">Risk Register</a>. You can filter by agent type to view DeepScan-specific findings separately from PR findings. All the same dismissal, fingerprinting, and suppression capabilities apply - findings dismissed as false positives from a DeepScan will be suppressed in future scans as well.</p>

<h2 id="triggering-a-deepscan">Triggering a DeepScan</h2>

<p>DeepScan can be triggered manually from the DryRun Security dashboard for any connected repository. It can also be triggered programmatically via the <a href="../api-guide.html">DryRun Simple API</a>, enabling integration into CI/CD pipelines or scheduled workflows.</p>
''',
}

PAGES['secrets-detection'] = {
    'title': 'Secrets Detection',
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

<h2 id="contextual-accuracy">Contextual Accuracy</h2>

<p>What distinguishes DryRun's secrets detection from simple regex scanning is context awareness. A string that matches the format of an AWS access key is not automatically a finding - the Secrets Analyzer considers whether it appears in a test fixture, an example configuration file, a comment marked as a placeholder, or a real configuration path being read at runtime. This dramatically reduces false positives without sacrificing genuine detection.</p>

<p>When a confirmed secret is found, the finding includes the file path, line number, and a plain-language explanation of the risk - without reproducing the credential value in the finding report itself.</p>

<h2 id="blocking-and-branch-protection">Blocking and Branch Protection</h2>

<p>The Secrets Analyzer can be configured to block PR merges via GitHub Branch Protection Rules. When a secret is detected and the Secrets Analyzer has blocking enabled, the check will fail and the PR cannot be merged until the credential is removed and the branch is re-scanned. See <a href="../configurations.html">Configurations</a> for setup instructions.</p>

<h2 id="suppression-and-false-positives">Suppression and False Positives</h2>

<p>Not every high-entropy string is a real credential. The Risk Register's <a href="../finding-dismissal.html">Finding Dismissal</a> workflow allows teams to mark findings as false positives with contextual notes - for example, to record that a particular string is a well-known public test key. Dismissed fingerprints are suppressed in future scans automatically.</p>
''',
}

PAGES['sca'] = {
    'title': 'Software Composition Analysis (SCA)',
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

<h2 id="sbom-integration">SBOM Integration</h2>

<p>DryRun Security's dependency analysis feeds into SBOM (Software Bill of Materials) generation, enabling you to produce a complete inventory of your software dependencies for compliance and audit purposes. See <a href="../sbom-generation.html">SBOM Generation</a> for details.</p>
''',
}

PAGES['iac-scanning'] = {
    'title': 'Infrastructure as Code Scanning',
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

<p>Like all DryRun Security analysis, IaC scanning is contextual. A finding is evaluated against the full intent of the infrastructure change - an intentionally public static asset bucket is treated differently from an accidentally public database. When your team uses <a href="../agents-md.html">AGENTS.md</a> to document known-safe infrastructure patterns, DryRun Security's agents apply that context during analysis to reduce false positives.</p>
''',
}

PAGES['coverage-matrix'] = {
    'title': 'Coverage Matrix - Vulnerability Categories',
    'description': 'The 47 vulnerability categories DryRun Security detects, with CWE mappings.',
    'section': 'Scanning',
    'content': '''
<p>This table lists the vulnerability categories DryRun Security can detect with the Code Review Agent. CWE mappings below are examples to help readers anchor each category to common weakness definitions.</p>

<p>We are always adding features and capabilities, and this list is updated accordingly.</p>

<h2 id="vulnerability-categories">Vulnerability Categories</h2>

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
    <tr><td>Intent Redirection</td><td>Unvalidated or unsafe redirection logic that can be abused to send users to unintended destinations.</td><td>CWE-601</td></tr>
    <tr><td>Language Version Risk</td><td>Use of outdated or unsupported programming language versions with known security issues.</td><td>CWE-1104</td></tr>
    <tr><td>LLM Tool Misuse</td><td>Unsafe or unintended use of large language model tools, including insecure prompt handling or tool misuse.</td><td>CWE-20, CWE-74, CWE-1426</td></tr>
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
    <tr><td>Subdomain Takeover</td><td>Dangling or misconfigured subdomains that can be claimed by attackers, as defined by Infrastructure as Code changes.</td><td>CWE-668, CWE-284</td></tr>
    <tr><td>Supply Chain Risk</td><td>Risks introduced through third-party libraries, dependencies, or external services.</td><td>CWE-1104, CWE-829</td></tr>
    <tr><td>Terminal Escape Injection</td><td>Injection of terminal control characters that can manipulate terminal output or behavior.</td><td>CWE-150, CWE-74</td></tr>
    <tr><td>Time-of-Check Time-of-Use (TOCTOU)</td><td>Race conditions where system state changes between validation and use.</td><td>CWE-367</td></tr>
    <tr><td>Timing Side Channel</td><td>Information leakage through measurable differences in execution time.</td><td>CWE-208</td></tr>
    <tr><td>UI Spoofing</td><td>User interface elements designed to deceive users into taking unintended actions.</td><td>CWE-451</td></tr>
    <tr><td>User Enumeration</td><td>Ability to determine valid users based on application responses.</td><td>CWE-203, CWE-204</td></tr>
    <tr><td>Vulnerable Dependency</td><td>Use of third-party dependencies with known security vulnerabilities.</td><td>CWE-937, CWE-1104</td></tr>
    <tr><td>XML Injection</td><td>Injection of malicious XML content that alters processing or behavior.</td><td>CWE-91</td></tr>
    <tr><td>Cross-Site Scripting (XSS)</td><td>Injection of malicious scripts that execute in a user's browser.</td><td>CWE-79</td></tr>
    <tr><td>XML External Entity (XXE)</td><td>XML parsing vulnerabilities that allow access to internal files or services.</td><td>CWE-611</td></tr>
  </tbody>
</table>
</div>
''',
}


# -- AI & Intelligence --

PAGES['ai-native-architecture'] = {
    'title': 'AI-Native Architecture',
    'description': "DryRun Security is built AI-first - a multi-agent system with specialized agents designed for every class of security analysis.",
    'section': 'AI & Intelligence',
    'content': '''
<h2 id="built-for-ai-not-bolted-on">Built for AI, Not Bolted On</h2>

<p>Most security tools began as rules engines, signature databases, or AST analyzers - and then added AI as a post-processing layer. DryRun Security was designed from the ground up as an AI-native system. Every component, from how code is ingested to how findings are reported, is built around the capabilities of large language models operating as specialized agents.</p>

<p>This architectural difference is fundamental. A rules engine with AI layered on top can summarize findings. An AI-native system can reason about code intent, trace data flows across files, evaluate the security implications of a business logic decision, and assess risk in the way a senior security engineer would - not by matching patterns, but by understanding context.</p>

<h2 id="multi-agent-system">Multi-Agent System</h2>

<p>DryRun Security's analysis is performed by a coordinated system of specialized agents. Each agent is designed for a specific domain of security analysis, allowing deep expertise without sacrificing coverage breadth.</p>

<p>Core agents include:</p>

<ul>
  <li><strong>Code Review Agent</strong> - The primary agent that analyzes pull request diffs for security vulnerabilities across all supported categories.</li>
  <li><strong>DeepScan Agent</strong> - Performs full-repository analysis, tracing multi-file data flows and identifying vulnerabilities that span across modules.</li>
  <li><strong>Policy Enforcement Agent</strong> - Evaluates code changes against user-defined Natural Language Code Policies and enforces organizational security standards.</li>
  <li><strong>Secrets Analyzer</strong> - Specialized detection of hardcoded credentials, API keys, and authentication tokens with contextual false-positive reduction.</li>
  <li><strong>SQL Injection Analyzer</strong> - Deep data-flow tracing for SQL injection vulnerabilities, covering both direct injection and ORM misuse patterns.</li>
  <li><strong>Infrastructure as Code Agent</strong> - Analyzes Terraform, CloudFormation, Kubernetes, and other IaC formats for misconfigurations and infrastructure security risks.</li>
  <li><strong>Dependency Risk Agent</strong> - Evaluates third-party packages and supply chain risk, including vulnerable dependency detection and SCA.</li>
</ul>

<h2 id="agentic-architecture">Agentic Architecture</h2>

<p>DryRun Security's agents operate with genuine agentic capability - they don't just classify code; they reason about it. An agent can decide to look up the definition of a called function, trace an import across files, or consult project-specific context from an <code>AGENTS.md</code> file before reaching a conclusion. This tool-use capability is what enables cross-file analysis and false-positive reduction that isn't possible with single-pass analysis.</p>

<p>Agents operate in parallel on each scan, with results coordinated into a unified report. This parallel architecture means that even complex repositories with many files and many potential findings can be analyzed quickly without sacrificing depth.</p>

<h2 id="model-independent-verification">Model-Independent Verification</h2>

<p>DryRun Security uses <strong>model-independent verification</strong> to validate findings before surfacing them. Candidate findings are cross-checked across multiple AI models, ensuring that a result is not an artifact of a single model's quirks or hallucination tendencies. This multi-model validation is a key part of why DryRun Security achieves significantly lower false-positive rates than single-model approaches.</p>

<p>This architecture also means DryRun Security is not locked to any single AI provider. As models improve and new capabilities emerge, DryRun Security can incorporate them without disrupting the underlying analysis framework.</p>
''',
}

PAGES['contextual-security-analysis'] = {
    'title': 'Contextual Security Analysis',
    'description': "A deep dive on DryRun Security's CSA methodology - what 'full context' means and why it changes what security analysis can find.",
    'section': 'AI & Intelligence',
    'content': '''
<h2 id="the-limits-of-pattern-matching">The Limits of Pattern Matching</h2>

<p>Pattern-matching SAST tools work by detecting syntactic patterns associated with known vulnerability classes. If you call <code>execute_query</code> with a string that contains user input, you get flagged. If you use an outdated encryption algorithm, you get flagged. The pattern is present; the finding is generated.</p>

<p>The fundamental problem is that security in real code is almost never a matter of syntactic patterns. Whether a SQL query is vulnerable depends on how the input was validated before it arrived. Whether a redirect is dangerous depends on whether the target URL can be influenced by an attacker. Whether an API endpoint is a risk depends on whether authorization is enforced - which might happen in middleware the pattern matcher never examined.</p>

<p>This is why traditional SAST produces so many false positives (flagging safe code) and so many false negatives (missing real vulnerabilities that don't match a pattern). It isn't a tuning problem. It's a fundamental limitation of the approach.</p>

<h2 id="what-full-context-means">What "Full Context" Means</h2>

<p>DryRun Security's Contextual Security Analysis evaluates code through several dimensions of context simultaneously:</p>

<h3 id="code-patterns-and-data-flow">Code Patterns and Data Flow</h3>
<p>CSA traces the flow of data from its origin (user input, external API, database read) through transformations and into sensitive operations. A function that receives a validated, sanitized parameter is treated differently from one that receives a raw request field, even if the calling code looks identical to a pattern matcher.</p>

<h3 id="runtime-behaviors">Runtime Behaviors</h3>
<p>CSA considers the runtime context of code: which framework is in use, how middleware is configured, what the deployment topology implies about trust boundaries. Code that relies on a WAF for input validation is different from code with no upstream protection, even if the application code itself looks the same.</p>

<h3 id="developer-intent">Developer Intent</h3>
<p>CSA evaluates what a code change is trying to accomplish. A change that adds a new authenticated API endpoint has very different security implications from a change that modifies how authentication is enforced on existing endpoints. Understanding intent is crucial for accurate severity assessment and for identifying when a change's security impact is larger than its visible footprint.</p>

<h3 id="cross-file-analysis">Cross-File Analysis</h3>
<p>Real vulnerabilities frequently span multiple files. The data entry point is in a controller. The validation logic is in a utility module. The dangerous operation is in a service layer. CSA follows these chains across file boundaries, providing the comprehensive view that single-file analysis fundamentally cannot.</p>

<h2 id="why-this-matters-operationally">Why This Matters Operationally</h2>

<p>The practical outcome of contextual analysis is findings that are accurate and actionable. When DryRun Security reports a vulnerability, it's because analysis of the full context concluded that a real risk exists - not because a pattern matched. When DryRun Security doesn't flag something, it's because the context indicates the code is actually safe.</p>

<p>This changes the developer experience. Security review stops being a noise-filtering exercise and becomes a focused list of genuine issues. Trust in the tool increases because findings are consistently meaningful. And the developers who receive findings have the context they need to understand and fix the issue - because the finding itself was generated by understanding that same context.</p>
''',
}

PAGES['business-logic-detection'] = {
    'title': 'Business Logic Detection',
    'description': 'How DryRun Security detects business logic flaws that pattern-matching tools fundamentally cannot find.',
    'section': 'AI & Intelligence',
    'content': '''
<h2 id="what-are-business-logic-flaws">What Are Business Logic Flaws?</h2>

<p>Business logic flaws are vulnerabilities that arise from errors in how an application implements its intended behavior - not from missing input validation or insecure library calls, but from flawed assumptions in the logic itself. They represent cases where the code does exactly what it was programmed to do, but what it was programmed to do creates a security risk.</p>

<p>Classic examples include: a price-calculation function that allows negative quantities to generate negative totals and reverse payment flows; an authorization check that verifies the user owns a resource but doesn't verify the user is modifying <em>their own</em> instance of that resource; a multi-step transaction that can be interrupted midway to leave the system in an inconsistent state that benefits the attacker.</p>

<p>No pattern matcher can find these. They don't involve known-vulnerable function calls or dangerous API usage. They require understanding what the code is supposed to do - and then evaluating whether it actually does it securely.</p>

<h2 id="how-dryrun-detects-logic-flaws">How DryRun Security Detects Logic Flaws</h2>

<p>DryRun Security's Code Review Agent and DeepScan Agent analyze code for business logic vulnerabilities by understanding application intent. When a PR modifies an e-commerce checkout flow, the agent evaluates the logic of the price calculation, discount application, and quantity validation as a unified behavior - not as individual function calls. It can identify cases where the logical chain has gaps that could be exploited.</p>

<p>This requires the kind of holistic code understanding that contextual AI analysis enables. The agent reads the code the way a security engineer would: with an understanding of what the feature is trying to accomplish, what inputs it receives, what outputs it produces, and what happens if those inputs are unexpected or adversarial.</p>

<h2 id="examples-of-what-it-catches">Examples of What It Catches</h2>

<ul>
  <li><strong>IDOR (Insecure Direct Object Reference)</strong> - An API endpoint that looks up a resource by user-controlled ID without verifying the requesting user owns that resource.</li>
  <li><strong>Race conditions in transactions</strong> - Logic that allows a resource to be consumed multiple times if requests arrive simultaneously, before a lock is applied.</li>
  <li><strong>Authorization on the wrong layer</strong> - UI-level access controls that aren't enforced at the API layer, allowing direct API calls to bypass restrictions.</li>
  <li><strong>State machine violations</strong> - Workflows that can be driven into invalid states by skipping or repeating steps in an unexpected order.</li>
  <li><strong>Privilege abuse paths</strong> - Sequences of otherwise-legitimate operations that, when combined, achieve an outcome an attacker shouldn't be able to reach.</li>
</ul>

<h2 id="why-this-matters">Why This Matters</h2>

<p>Business logic flaws are responsible for some of the most significant security breaches in modern applications - particularly in fintech, e-commerce, and any domain where the application itself mediates valuable transactions or sensitive data access. Because these vulnerabilities don't match any CVE or pattern signature, they persist in codebases for months or years until discovered through manual penetration testing or in production exploitation.</p>

<p>DryRun Security brings automated business logic analysis into the PR review workflow, giving development teams a systematic way to catch these vulnerabilities before they reach production.</p>
''',
}

PAGES['git-behavioral-analysis'] = {
    'title': 'Git Behavioral Analysis',
    'description': "DryRun Security analyzes git commit patterns and developer behavior as a security signal - a capability unique to DryRun.",
    'section': 'AI & Intelligence',
    'content': '''
<h2 id="git-history-as-security-signal">Git History as a Security Signal</h2>

<p>Every commit, every PR, every branch - the git history of a repository is a rich record of developer activity. Most security tools treat this as irrelevant background; they care only about the current state of the code. DryRun Security takes a different view: developer behavior patterns are a meaningful security signal, and understanding them enables a class of detection that code analysis alone cannot provide.</p>

<p>When code changes arrive in a pull request, DryRun Security doesn't just analyze the diff in isolation. It evaluates the change in the context of the developer's history, the repository's patterns, and the behavioral characteristics of the change itself. This enables detection of anomalies that indicate elevated risk - not because the code contains a known vulnerability, but because the circumstances surrounding the code change are unusual.</p>

<h2 id="what-behavioral-analysis-detects">What Behavioral Analysis Detects</h2>

<p>Git behavioral analysis contributes to DryRun Security's risk assessment in several ways:</p>

<h3 id="unusual-change-patterns">Unusual Change Patterns</h3>
<p>A commit that modifies authentication logic, authorization enforcement, and audit logging simultaneously - and does so in a way inconsistent with the developer's historical coding style - warrants closer scrutiny than the same code changes arriving individually over time. Behavioral context raises the signal strength of findings.</p>

<h3 id="sensitive-path-modifications">Sensitive Path Modifications</h3>
<p>Changes to security-critical files (authentication modules, cryptographic utilities, authorization middleware) are flagged with higher priority when they originate from contributors who don't typically modify those paths, or when they arrive outside of normal development patterns for the repository.</p>

<h3 id="supply-chain-risk-indicators">Supply Chain Risk Indicators</h3>
<p>In the context of AI-generated code and automated tooling, behavioral analysis helps identify when changes have characteristics inconsistent with the human developer's normal patterns - an important signal for detecting potential compromise or malicious code injection.</p>

<h2 id="unique-capability">A Unique Capability</h2>

<p>No other application security tool routinely incorporates git behavioral analysis as a security signal. Most tools are designed to analyze the current state of code, not the behavioral context of how that code arrived. DryRun Security's integration of behavioral signals with code analysis represents a genuinely different approach to software supply chain security - one that treats the development process itself as part of the threat model.</p>

<h2 id="privacy-and-developer-trust">Privacy and Developer Trust</h2>

<p>Behavioral analysis is designed to augment security findings, not to monitor individual developers. The analysis is used to prioritize and contextualize security findings - never to generate reports about individual developer behavior or to create surveillance capabilities. The goal is better security outcomes, not productivity monitoring.</p>
''',
}

PAGES['code-security-knowledge-graph'] = {
    'title': 'Code Security Knowledge Graph',
    'description': "DryRun Security builds a durable knowledge graph of code security intelligence that persists across scans and improves over time.",
    'section': 'AI & Intelligence',
    'content': '''
<h2 id="beyond-stateless-scanning">Beyond Stateless Scanning</h2>

<p>Most security scanning tools are stateless: they analyze a PR, produce findings, and forget everything. The next PR is analyzed completely fresh, with no memory of what was found before, what was dismissed as a false positive, or how the codebase has evolved over time. This means every scan starts from zero, and every improvement to accuracy must be re-learned.</p>

<p>DryRun Security builds and maintains a <strong>Code Security Knowledge Graph</strong> - a persistent, structured representation of security intelligence about your codebase that accumulates over time and informs every subsequent analysis.</p>

<h2 id="what-the-knowledge-graph-contains">What the Knowledge Graph Contains</h2>

<p>The knowledge graph captures and connects multiple dimensions of security knowledge about your repositories:</p>

<ul>
  <li><strong>Finding history</strong> - Which vulnerabilities have been identified, when, in which files, and what their current disposition is (open, dismissed, fixed).</li>
  <li><strong>False positive suppression</strong> - When a finding is dismissed as a false positive, that judgment is encoded as a fingerprint and applied to suppress the same finding in future scans automatically.</li>
  <li><strong>Developer-provided context</strong> - Context added by developers and security teams when dismissing findings is stored and used to calibrate future analysis in similar situations.</li>
  <li><strong>Codebase patterns</strong> - Understanding of the frameworks, authentication patterns, and security-relevant design choices in your codebase that inform how code changes should be evaluated.</li>
</ul>

<h2 id="model-independent-verification">Model-Independent Verification</h2>

<p>The knowledge graph is maintained independently of any single AI model. This is a deliberate architectural choice. AI models change - they're updated, replaced, and improved. DryRun Security's findings and the intelligence encoded in the knowledge graph persist across model changes, ensuring continuity of security coverage even as the underlying AI infrastructure evolves.</p>

<p>Model-independent verification also means findings are validated across multiple models before being surfaced. The knowledge graph records verified findings, not model outputs - the distinction matters for reliability and auditability.</p>

<h2 id="accumulating-accuracy-over-time">Accumulating Accuracy Over Time</h2>

<p>The practical impact of the knowledge graph is that DryRun Security gets more accurate over time as it learns the specific characteristics of your codebase. False positive rates decrease as the system accumulates dismissal context. The risk model becomes better calibrated to your specific risk profile, frameworks, and deployment patterns. Security intelligence is a durable organizational asset - not something that evaporates between scans.</p>
''',
}

PAGES['natural-language-code-policies'] = {
    'title': 'Natural Language Code Policies',
    'description': 'Create and enforce security policies for your codebase using plain English - no custom rule languages or complex scripting required.',
    'section': 'AI & Intelligence',
    'content': '''
<p>DryRun Security's Natural Language Code Policies (NLCPs) are a way to define and enforce security policies in a codebase using natural language instead of complex scripting or specialized rule languages.</p>

<p>In this section we demonstrate how to build and save a Natural Language Code Policy in the DryRun Security Dashboard.</p>

<h2 id="creating-a-policy">Creating a Policy</h2>

<ol>
  <li>Log in to the DryRun Security portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</li>
  <li>Navigate to the <strong>Code Policies</strong> section. You'll see a list of previously saved Code Policies.</li>
  <li>Click <strong>Add New Code Policy</strong>. You'll see the Code Policy Builder, which can be used to evaluate and save a Natural Language Code Policy.</li>
  <li>Enter a <strong>Name</strong> for the policy.</li>
  <li>Choose a <strong>Repository</strong> and <strong>Pull Request</strong> to evaluate.</li>
  <li>Enter the Natural Language Code Policy details:
    <ul>
      <li><strong>Question</strong> (required): A natural language question that identifies whether a specific change relates to the policy. For example, "Does this change expose any sensitive data?"</li>
      <li><strong>Background</strong> (optional): Background information or examples that may be used to refine the evaluation. For example, "We are concerned about..."</li>
      <li><strong>Guidance</strong> (optional): Additional information on actions to take when the policy condition is met.</li>
    </ul>
  </li>
  <li>Click <strong>Run</strong> to see the results of the Code Policy evaluation.</li>
  <li>Once the policy is returning expected results, click <strong>Save</strong> to save it for use in a Repository configuration.</li>
</ol>

<p>To apply the Code Policy to one or more repositories, click <strong>Configure</strong> and follow the steps in <a href="./configurations.html">Configure Repositories</a>.</p>

<h2 id="policy-enforcement-agent">Policy Enforcement Agent</h2>

<p>When a pull request is opened, DryRun Security's Policy Enforcement Agent runs all configured Natural Language Code Policies for the repository. The Policy Enforcement Agent can run up to 7 code policies per repository. Results appear in the PR comment and in the GitHub Checks area, with the option to block merges when a policy has findings.</p>

<h2 id="next-steps">Next Steps</h2>

<ul>
  <li>See the <a href="./nlcp-starter-pack.html">NLCP Starter Pack</a> for ready-to-use policy examples.</li>
  <li>See <a href="./nlcp-best-practices.html">NLCP Best Practices</a> for guidance on writing effective policy backgrounds.</li>
  <li>See <a href="./configurations.html">Configurations</a> to attach policies to repositories.</li>
</ul>
''',
}

PAGES['nlcp-starter-pack'] = {
    'title': 'NLCP Starter Pack',
    'description': 'Ready-to-use Natural Language Code Policy templates to get started quickly. Customize for your organization or use as-is.',
    'section': 'AI & Intelligence',
    'content': '''
<p>The following Natural Language Code Policies can be used to help you get started. They are generic enough to be customized by your organization but can also be used as-is.</p>

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
''',
}

PAGES['nlcp-best-practices'] = {
    'title': 'NLCP Best Practices',
    'description': 'Examples of what to do and what to avoid when writing the Background for your Natural Language Code Policies.',
    'section': 'AI & Intelligence',
    'content': '''
<p>When you provide more clarity in your Natural Language Code Policy's background, your policy becomes more reliable and accurate. The tips below help your policies accurately scope which files are considered, reason about your code, and decide when deeper analysis is necessary.</p>

<h2 id="what-is-a-background">What Is a Background?</h2>

<p>When writing your Natural Language Code Policy, you provide:</p>
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
''',
}


# -- Remediation --

PAGES['auto-fix'] = {
    'title': 'Auto-Fix',
    'description': 'DryRun Security generates AI-powered fix suggestions that match your codebase patterns, making remediation fast and consistent.',
    'section': 'Remediation',
    'content': '''
<h2 id="from-finding-to-fix">From Finding to Fix</h2>

<p>Identifying a vulnerability is only half the work. Developers still need to understand what the fix is, implement it correctly, and verify that the fix doesn't introduce new problems. For high-volume security tools, the remediation burden can be the biggest obstacle to actually improving security posture - teams become skilled at triaging findings rather than closing them.</p>

<p>DryRun Security's <strong>Auto-Fix</strong> capability closes this gap by generating AI-powered remediation suggestions directly alongside each finding. When a vulnerability is identified, DryRun Security analyzes the affected code, understands the vulnerability's root cause, and generates a concrete fix that can be applied to resolve it.</p>

<h2 id="contextual-fixes">Contextual Fixes That Match Your Code</h2>

<p>Auto-Fix suggestions are generated in the context of your specific codebase - not from a generic template. The fix generation process considers:</p>

<ul>
  <li>The frameworks, libraries, and language idioms your code uses</li>
  <li>The existing patterns in your codebase for similar problems (if you validate input one way elsewhere, the fix follows the same pattern)</li>
  <li>The surrounding code structure and dependencies that a fix must integrate with</li>
  <li>Security best practices for the specific vulnerability class</li>
</ul>

<p>The result is a fix suggestion that a developer can evaluate and apply with confidence - not a generic "sanitize this input" suggestion that still requires significant interpretation.</p>

<h2 id="fix-presentation">How Fix Suggestions Are Presented</h2>

<p>Auto-Fix suggestions appear inline with findings in the PR comment and in the DryRun Security dashboard. Each suggestion includes:</p>

<ul>
  <li>The specific code change recommended (shown as a diff)</li>
  <li>An explanation of why this fix addresses the vulnerability</li>
  <li>Any relevant considerations the developer should be aware of before applying</li>
</ul>

<h2 id="verification">Verification After Fixing</h2>

<p>After a fix is applied and the PR is updated, DryRun Security automatically re-analyzes the affected code to verify that the vulnerability has been resolved and that the fix hasn't introduced new issues. See <a href="./fix-verification.html">Fix Verification</a> for details on how this works.</p>
''',
}

PAGES['fix-verification'] = {
    'title': 'Fix Verification',
    'description': 'After a fix is applied, DryRun Security re-tests to confirm the vulnerability is resolved and no regressions were introduced.',
    'section': 'Remediation',
    'content': '''
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

PAGES['finding-dismissal'] = {
    'title': 'Finding Dismissal',
    'description': 'Dismiss false positives with context, suppress recurring findings with fingerprinting, and manage risk through developer and security team workflows.',
    'section': 'Remediation',
    'content': '''
<p>Risk Register supports Finding Dismissal so teams can formally close out incorrect findings and reduce noise over time. Dismissed findings are fingerprinted and suppressed in future scans automatically.</p>

<h2 id="dismissing-a-finding">Dismissing a Finding</h2>

<p>In the Risk Register, click <strong>Dismiss</strong> on a finding to:</p>
<ul>
  <li>Select a reason for dismissal (for example: False Positive, Won't Fix)</li>
  <li>Add supporting context in a text box</li>
</ul>

<h2 id="false-positive-fingerprinting">False Positive Fingerprinting</h2>

<p>When you dismiss a finding as <strong>False Positive</strong>:</p>
<ul>
  <li>DryRun Security creates a fingerprint of that vulnerability.</li>
  <li>Future PR and DeepScans will suppress the finding when the same fingerprint is detected, so it doesn't come back.</li>
</ul>

<h2 id="context-suppression">Context-Based Suppression</h2>

<p>When you include context in the text box:</p>
<ul>
  <li>That context is stored and used in future evaluations to further suppress like or similar false positives.</li>
  <li>This is useful for cases where a finding is safe because of your framework behavior, implementation pattern, or deployment topology.</li>
</ul>

<p>Examples of useful context:</p>
<ul>
  <li>"This endpoint is only accessible from internal services - no user input reaches this code path."</li>
  <li>"TLS offloading is handled upstream; the application does not need to enforce HTTPS internally."</li>
  <li>"This query is constructed only from validated constants, never from user input."</li>
</ul>

<h2 id="dismissal-from-pr-workflow">Dismissal from the PR Workflow</h2>

<p>Developers can also mark findings as False Positive and add context from the developer comment workflow in GitHub and GitLab. Those dismissals flow into the Risk Register and are applied to future scans the same way - keeping the feedback loop close to where developers work.</p>

<h2 id="faqs">FAQs</h2>

<p><strong>What is Finding Dismissal?</strong><br>
Finding Dismissal lets you dismiss a finding and record why, using a dismissal reason and optional context. Dismissed findings are marked resolved in the UI.</p>

<p><strong>What happens when I dismiss a finding as a False Positive?</strong><br>
DryRun Security fingerprints the vulnerability. If the same fingerprint is detected in a future PR or DeepScan, the finding is automatically suppressed.</p>

<p><strong>How is the context field used?</strong><br>
Context is stored with the dismissal and used in future scan evaluations to further suppress like or similar false positives.</p>

<p><strong>Can developers dismiss findings too?</strong><br>
Yes. Developers can mark findings as False Positive from GitHub and GitLab comments. Those dismissals are synced to the Risk Register.</p>
''',
}


# -- Platform --

PAGES['risk-register'] = {
    'title': 'Risk Register',
    'description': 'One view to see, search, and act on all security risk across your organization.',
    'section': 'Platform',
    'content': '''
<p>Risk Register centralizes findings from PR scans and DeepScans. It gives AppSec, DevSecOps, and engineering leaders a clear starting point to track, triage, and act on risk across the entire organization.</p>

<h2 id="risk-register-features">Risk Register Features</h2>

<ul>
  <li>See all findings from all PRs and DeepScans together.</li>
  <li>Understand where risk is concentrated by repo, type, and severity.</li>
  <li>Prioritize work by Critical/High first, then drill into specifics.</li>
  <li>Dismiss findings with reasons and context so the same false positives do not keep coming back.</li>
  <li>Use filters to move from org-level insight to actionable lists in seconds:
    <ul>
      <li>Date ranges</li>
      <li>Risk level (Critical, High, Medium, Low)</li>
      <li>Agent (DeepScan, PR)</li>
      <li>Status (Merged, Open, Closed)</li>
    </ul>
  </li>
</ul>

<h2 id="finding-dismissal">Finding Dismissal</h2>

<p>Risk Register supports Finding Dismissal so teams can formally close out incorrect findings and reduce noise over time. See <a href="../finding-dismissal.html">Finding Dismissal</a> for the full workflow.</p>

<p>In the Risk Register, click <strong>Dismiss</strong> on a finding to select a dismissal reason and optionally add context. When you dismiss a finding as <strong>False Positive</strong>, DryRun Security creates a fingerprint of that vulnerability and suppresses it in future scans automatically.</p>

<h2 id="faqs">FAQs</h2>

<p><strong>How are severities determined?</strong><br>
DryRun Security normalizes outputs to Critical/High/Medium/Low. For PR scans, this aligns closely with Fail, Risky, Info, and other labels. DeepScan uses its own severity model and outputs are normalized similarly.</p>

<p><strong>Which columns can I sort?</strong><br>
Risk is sortable. Type, File, Repo, Detected Date, Agent, and PR Status are sortable as well.</p>

<p><strong>What filters are available?</strong><br>
Filter by Date range, Risk level, Agent (DeepScan, PR), and Status (Merged, Open, Closed).</p>
''',
}

PAGES['security-dashboard'] = {
    'title': 'Security Dashboard',
    'description': 'Overview of the DryRun Security Dashboard - analytics, risk trending, findings overview, and repository-level insights.',
    'section': 'Platform',
    'content': '''
<h2 id="your-security-command-center">Your Security Command Center</h2>

<p>The DryRun Security Dashboard provides a unified view of your organization's security posture. From a single interface, AppSec leads and engineering managers can understand where risk is concentrated, how it's trending over time, which repositories need attention, and what your team has been doing to address findings.</p>

<p>The dashboard is designed to support both strategic and tactical security work. At the strategic level, it provides the trend data and aggregate visibility needed to report to leadership and make prioritization decisions. At the tactical level, it gives engineers and security reviewers the filtered views they need to work through findings efficiently.</p>

<h2 id="analytics-overview">Analytics Overview</h2>

<p>The Dashboard's analytics view provides aggregate metrics across your connected repositories:</p>

<ul>
  <li><strong>Total findings</strong> by severity (Critical, High, Medium, Low), with trend lines showing how these numbers have changed over your selected time window</li>
  <li><strong>Finding velocity</strong> - how many new findings are being introduced versus how many are being closed or dismissed</li>
  <li><strong>Coverage metrics</strong> - what percentage of PRs across your organization are being scanned, and scan volume over time</li>
  <li><strong>Agent breakdown</strong> - which security agents are generating the most findings, identifying which vulnerability classes are most prevalent in your codebase</li>
</ul>

<h2 id="repository-level-insights">Repository-Level Insights</h2>

<p>Drilling down to the repository level reveals the specific security posture of individual codebases. Each repository view shows:</p>

<ul>
  <li>Open findings by severity and type</li>
  <li>Recent PR scan history with results</li>
  <li>DeepScan history and current finding baseline</li>
  <li>Risk trend for the repository over time</li>
  <li>Configuration settings currently applied</li>
</ul>

<h2 id="risk-trending">Risk Trending</h2>

<p>The dashboard's risk trending view shows how your organization's security posture evolves over time. Compare periods, identify regressions, and track the impact of security initiatives. See <a href="./risk-trending.html">Risk Trending</a> for a deeper explanation of how trend analysis works.</p>

<h2 id="ai-assistance">AI Assistance</h2>

<p>The Insights page includes an AI Assistance feature that lets admins ask natural language questions about their security data - "What were the biggest findings last week?" or "Which PR introduced the risky dependency?" See <a href="./ai-insights.html">AI Insights</a> for full documentation.</p>
''',
}

PAGES['configurations'] = {
    'title': 'Configure Repositories',
    'description': 'Customize DryRun Security behavior per repository - enable agents, attach policies, configure blocking, and set up notifications.',
    'section': 'Platform',
    'content': '''
<p>In this section we demonstrate how to customize the behavior of DryRun Security by creating a Configuration in the Dashboard.</p>

<h2 id="creating-a-configuration">Creating a Configuration</h2>

<ol>
  <li>Log in to the DryRun Security portal at <a href="https://app.dryrun.security" target="_blank" rel="noopener noreferrer">https://app.dryrun.security</a>.</li>
  <li>Navigate to <strong>Settings &gt; Configuration</strong>.
    <br><strong>Note:</strong> The <code>default</code> configuration is editable and applies to all repositories not included in another configuration.</li>
  <li>Click <strong>Add new Configuration +</strong>.</li>
  <li>Set up the new configuration:
    <ul>
      <li>Enter a name for the configuration.</li>
      <li>Use the <strong>Select Repositories</strong> selector to choose which repositories will use this configuration.
        <br><strong>Note:</strong> Repositories can only have a single configuration. Repositories already in another configuration will be greyed out.</li>
      <li>Enable or disable the DryRun Security Pull Request Comment.</li>
      <li>Enable or disable Notifications. If enabled, choose the integrations to apply.</li>
      <li>Add Code Policies by clicking <strong>Add Policy +</strong>. The Policy Enforcement Agent can run up to 7 code policies per repository.</li>
      <li>Configure Code Policy settings: enable <strong>Blocking</strong>, set <strong>Silent Mode</strong>, and choose the <strong>Risk Level</strong> returned when the policy has findings (Info, Risky, or Fail).</li>
      <li>Configure Code Security Agents: enable or disable individual agents, set <strong>Blocking</strong>, and configure <strong>Silent Mode</strong>.</li>
    </ul>
  </li>
  <li>Click <strong>Save</strong>.</li>
</ol>

<h2 id="configure-blocking">Configure Blocking for Code Policies</h2>

<p>Both Natural Language Code Policies and Code Security Agents can be used with GitHub Branch Protection Rules to block PRs from being merged. After enabling <strong>Blocking</strong>, follow these steps:</p>

<h3 id="set-up-branch-protection">Set Up a Classic Branch Protection Rule</h3>

<ol>
  <li>On GitHub, navigate to the main page of the repository.</li>
  <li>Under your repository name, click <strong>Settings</strong>.</li>
  <li>In the <strong>Code and automation</strong> section of the sidebar, click <strong>Branches</strong>.</li>
  <li>Choose <strong>Add classic branch protection rule</strong>.</li>
  <li>Under <strong>Branch name pattern</strong>, type the name of the branch to protect (e.g., <code>main</code>).</li>
  <li>Select <strong>Require status checks to pass before merging</strong>.</li>
  <li>In the search field, search for DryRun Security status checks to require. Choose <strong>Code Policies</strong> for Natural Language Code Policies, or the agent name (e.g., <strong>Secrets Analyzer</strong>) for Code Security Agents.</li>
  <li>Click <strong>Create</strong>.</li>
</ol>

<p>When a Natural Language Code Policy has <strong>Blocking</strong> enabled, it appears as a single Check in GitHub under the name <strong>Code Policies</strong>. When a Code Security Agent has blocking enabled, it appears as a Check with the agent's name (e.g., <strong>Secrets Analyzer</strong>).</p>
''',
}

PAGES['notifications'] = {
    'title': 'Notifications',
    'description': 'Set up Slack and webhook integrations to receive security alerts from DryRun Security when findings meet your configured risk threshold.',
    'section': 'Platform',
    'content': '''
<p>In this section we set up an integration webhook and use it to receive event notifications from DryRun Security. There is a dedicated Slack integration and a Generic webhook option. The configuration steps are identical for both.</p>

<p><strong>Prerequisite:</strong> You'll need to have already created a Webhook URL on the system you wish to integrate. Messages sent are JSON-formatted POST requests.</p>

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
''',
}

PAGES['ai-insights'] = {
    'title': 'AI Insights',
    'description': 'Ask natural language questions about your security data - findings, PRs, vulnerabilities, and trends - powered by AI.',
    'section': 'Platform',
    'content': '''
<p>AI Assistance is an admin-only chat experience inside the Insights page in the DryRun Security dashboard. It lets you ask natural language questions about your repos, pull requests, vulnerabilities, and analyzer findings, then pulls answers from your organization's Insights data using built-in tools.</p>

<h2 id="what-its-for">What It's For</h2>

<p>Use AI Assistance when you want fast, plain English answers to questions like:</p>
<ul>
  <li>"What changed this week?"</li>
  <li>"Which PR introduced the risky dependency?"</li>
  <li>"What are the top risks across my repos right now?"</li>
</ul>

<h2 id="key-points">Key Points</h2>

<ul>
  <li><strong>Admin only access:</strong> Only admin users can use AI Assistance.</li>
  <li><strong>Built for AppSec and developers:</strong> Ask about risks, PRs, vulnerabilities, integrations, and code changes.</li>
  <li><strong>30-day window per query:</strong> Each tool call supports up to a 30-day time range. Use repeated calls for longer spans.</li>
  <li><strong>Parallel lookups:</strong> Some workflows can call multiple tools at once.</li>
</ul>

<h2 id="ways-to-use">Ways to Use AI Assistance</h2>

<h3 id="search-insights">Search Across Insights</h3>
<p>Answer questions across wide-ranging security insights - vulnerabilities, integrations, key risks, or code patterns. Best for broad searches when you're exploring what is happening or what changed.</p>
<p><em>Example: "Tell me the top risks in this week's deployments." "Any new payment processing code added recently?"</em></p>

<h3 id="summarize-insights">Summarize Insights for a Time Range</h3>
<p>Pull together a summary of critical security insights for a given time range and organization. Best for big-picture views before you drill into specifics.</p>
<p><em>Example: "What were the biggest findings in my repositories last week?" "Overview of vulnerabilities identified this month across all projects."</em></p>

<h3 id="pr-deep-dive">Pull Request Deep Dive</h3>
<p>Dive into the details of a specific pull request. Best for investigating what happened in a PR, why it was flagged, and what to fix.</p>
<p><em>Example: "What security issues were raised in PR #135?" "Was PR #104 flagged for any credential exposures?"</em></p>

<h3 id="analyzer-stats">Analyzer Stats and Trends</h3>
<p>Fetch stats from analyzers detecting security threats like SQL injection, insecure dependencies, IDOR, and more.</p>
<p><em>Example: "How many vulnerabilities were detected by the SQL Injection Analyzer last week?" "Show stats for threats in repository 'dryrun-api' for December."</em></p>

<h3 id="file-level-data">File Level Security Data and History</h3>
<p>Inspect security-relevant data and history for an individual file.</p>
<p><em>Example: "Give me security data for src/login.js." "What's the history of vulnerabilities linked to src/config.yml?"</em></p>

<h2 id="common-workflows">Common Workflows</h2>

<h3 id="weekly-risk-review">Weekly Risk Review</h3>
<ol>
  <li>Run a summary for the last 7 days.</li>
  <li>Use a broad search to expand on the top risks.</li>
  <li>Drill into suspicious PRs with a pull request deep dive.</li>
</ol>

<h3 id="trend-reporting">Trend Reporting</h3>
<ol>
  <li>Pull analyzer stats for the last 30 days.</li>
  <li>Repeat for prior windows (e.g., previous month).</li>
  <li>Compare trends and summarize changes.</li>
</ol>
''',
}

PAGES['risk-trending'] = {
    'title': 'Risk Trending',
    'description': 'Track security posture over time, compare periods, and identify regression with DryRun Security risk trending.',
    'section': 'Platform',
    'content': '''
<h2 id="continuous-security-baseline">Continuous Security Baseline</h2>

<p>Point-in-time security assessments give you a snapshot of your security posture on the day the assessment runs. But software is always changing - new code is deployed, old vulnerabilities are closed, new ones are introduced. Understanding whether your organization's security is improving or degrading over time requires continuous measurement, not periodic snapshots.</p>

<p>DryRun Security automatically builds and maintains a continuous security baseline for every connected repository. As scans run - on each pull request and each DeepScan - findings are recorded and trend data is updated. This creates a running picture of security posture that you can interrogate at any level of granularity: the full organization, a specific team, a single repository, or a particular vulnerability class.</p>

<h2 id="comparing-periods">Comparing Periods</h2>

<p>Risk trending allows you to select any two time periods and compare them directly. Common comparisons include:</p>

<ul>
  <li><strong>Week over week</strong> - Are you introducing new findings faster than you're closing old ones? Is the mix of severities changing?</li>
  <li><strong>Sprint over sprint</strong> - Are security remediation efforts keeping pace with development velocity?</li>
  <li><strong>Quarter over quarter</strong> - Is the security program producing measurable improvement in overall risk posture?</li>
  <li><strong>Before and after an initiative</strong> - Did the shift-left push, the security training, or the new policy configuration actually change outcomes?</li>
</ul>

<h2 id="identifying-regression">Identifying Regression</h2>

<p>Risk trending surfaces regression early. If a repository's finding rate spikes or a new vulnerability class begins appearing frequently, trend analysis will show the inflection point - making it easier to identify which changes or teams introduced the regression and prioritize remediation accordingly.</p>

<h2 id="reporting">Reporting</h2>

<p>Trend data is available through the DryRun Security dashboard and via the <a href="./api-guide.html">Simple API</a> for integration into your own reporting systems, security scorecards, or executive dashboards. Organizations using DryRun Security for compliance purposes can use trend reports as evidence of continuous monitoring and improving security posture over time.</p>
''',
}

PAGES['sbom-generation'] = {
    'title': 'SBOM Generation',
    'description': 'Generate Software Bill of Materials (SBOM) and AI-BOM for compliance, audit readiness, and supply chain transparency.',
    'section': 'Platform',
    'content': '''
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


# -- Developer Tools --

PAGES['ide-integration'] = {
    'title': 'IDE Integration',
    'description': 'DryRun Security integrates with VS Code, Cursor, and other IDEs - bringing security intelligence into your development environment.',
    'section': 'Developer Tools',
    'content': '''
<h2 id="security-in-your-editor">Security in Your Editor</h2>

<p>The earlier in the development process a vulnerability is caught, the cheaper it is to fix. DryRun Security's IDE integration brings security analysis into the development environment itself - the place where developers spend most of their time writing and reviewing code.</p>

<p>Rather than waiting for a PR to be opened to receive security feedback, developers with the IDE integration can get security context inline as they work - understanding the security implications of the code they're writing and the codebase they're modifying without leaving their editor.</p>

<h2 id="vs-code-and-cursor">VS Code and Cursor</h2>

<p>DryRun Security integrates with Visual Studio Code and Cursor through two complementary mechanisms:</p>

<h3 id="mcp-integration">MCP Integration</h3>
<p>The DryRun Security Insights MCP (Model Context Protocol) server connects your IDE's AI assistant directly to your organization's security data. When coding in Cursor or GitHub Copilot in VS Code, the AI assistant can answer security questions about your codebase, pull up findings for files you're working on, and provide context about your organization's security posture. See <a href="./mcp-integration.html">MCP Integration</a> for configuration details.</p>

<h3 id="direct-extension">Direct Extension</h3>
<p>The DryRun Security extension surfaces security findings from your most recent scans inline in your editor, showing you open findings for the file you're currently editing without requiring you to switch to the dashboard. Findings from both PR scans and DeepScans are available.</p>

<h2 id="ai-native-ide">AI-Native IDE Workflows</h2>

<p>For teams using AI coding assistants like Cursor, GitHub Copilot, or Claude Code, the DryRun Security IDE integration is particularly valuable. It allows the AI assistant to query DryRun Security's security intelligence as part of code generation - helping AI assistants write more secure code by understanding what vulnerabilities have been found in the codebase and what security patterns are in use.</p>

<p>This is especially relevant as teams adopt <code>AGENTS.md</code> to guide AI coding agents. See <a href="./agents-md.html">AGENTS.md</a> for how to configure security guidelines that AI agents and DryRun Security both use.</p>
''',
}

PAGES['mcp-integration'] = {
    'title': 'MCP Integration',
    'description': 'Connect AI assistants to DryRun Security insights using the Model Context Protocol for natural language queries about your security data.',
    'section': 'Developer Tools',
    'content': '''
<p>The DryRun Security Insights MCP enables AI assistants to securely connect to your organization's security data for powerful, context-aware code analysis. Think of it as "USB-C for AI" - a standard way for agents to interact with security insights, trends, and context across your codebase.</p>

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

<h3 id="direct-http">Direct HTTP Configuration (Recommended)</h3>

<p>If your client supports HTTP-based MCP servers with OAuth, connect directly:</p>

<pre><code>{
  "mcpServers": {
    "dryrun-security": {
      "type": "http",
      "url": "https://insights-mcp.dryrun.security/insights/mcp"
    }
  }
}</code></pre>

<h3 id="cursor-notice">Cursor Compatibility Notice</h3>

<p><strong>Known issue:</strong> Cursor currently has a known bug in its MCP implementation that may cause authentication failures. Contact <a href="mailto:hi@dryrun.security">hi@dryrun.security</a> if you need the workaround enabled for your environment.</p>

<h3 id="claude-shortcuts">Claude Shortcuts</h3>

<p><strong>Claude Code (CLI):</strong></p>
<pre><code>claude mcp add --transport http dryrun-security https://insights-mcp.dryrun.security/insights/mcp</code></pre>

<p><strong>Claude Desktop or Claude Web:</strong></p>
<ol>
  <li>Navigate to <a href="https://claude.ai" target="_blank" rel="noopener noreferrer">https://claude.ai</a>.</li>
  <li>Select <strong>Settings</strong>.</li>
  <li>Select <strong>Connectors</strong>.</li>
  <li>Click <strong>Add custom connector</strong>.</li>
  <li>Enter the URL: <code>https://insights-mcp.dryrun.security/insights/mcp</code></li>
  <li>Select <strong>Add</strong>.</li>
</ol>

<h3 id="mcp-remote">Using mcp-remote (Fallback)</h3>

<p>For clients that don't support HTTP-based MCP servers or if you experience authentication issues, use <a href="https://github.com/geelen/mcp-remote" target="_blank" rel="noopener noreferrer">mcp-remote</a>. Requires Node.js.</p>

<pre><code>{
  "mcpServers": {
    "dryrun-security": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://insights-mcp.dryrun.security/insights/mcp",
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

<p>When you first start the DryRun Security Insights MCP, you'll be prompted in a browser to authorize the <code>dryrunsecurity-insights-mcp</code> GitHub OAuth application. Click the <strong>Grant</strong> button to grant access to the appropriate GitHub Organization.</p>

<h2 id="verifying">Verifying the Connection</h2>

<p>Once configured, confirm the DryRun Security Insights tool is available in your AI assistant's toolset. Try asking: <em>"What is my insights summary for the past week?"</em></p>

<p>If you encounter any issues, reach out at <a href="mailto:hi@dryrun.security">hi@dryrun.security</a>.</p>
''',
}

PAGES['agents-md'] = {
    'title': 'AGENTS.md',
    'description': 'Use AGENTS.md to provide security context to DryRun Security Code Review and DeepScan agents.',
    'section': 'Developer Tools',
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

PAGES['cicd-integration'] = {
    'title': 'CI/CD Integration',
    'description': 'Integrate DryRun Security into CI/CD pipelines - use GitHub Branch Protection to block merges and enforce security gates.',
    'section': 'Developer Tools',
    'content': '''
<h2 id="dryrun-in-your-pipeline">DryRun Security in Your Pipeline</h2>

<p>DryRun Security integrates natively with GitHub and GitLab CI/CD workflows. Because DryRun Security is a GitHub App (and a GitLab integration), it participates directly in the pull request and pipeline status check system - no additional CI/CD configuration is required to get basic integration. Every PR scan automatically posts a status check result that your pipeline infrastructure can act on.</p>

<h2 id="github-branch-protection">GitHub Branch Protection Rules</h2>

<p>The most common CI/CD integration pattern is using GitHub Branch Protection Rules to prevent vulnerable code from being merged into protected branches. DryRun Security supports this through the <strong>Blocking</strong> configuration on both Code Policies and Code Security Agents.</p>

<p>When a Code Policy or Agent has <strong>Blocking</strong> enabled:</p>
<ol>
  <li>DryRun Security posts a failing status check to the PR when findings exceed the configured risk threshold.</li>
  <li>Your Branch Protection Rule requires this check to pass before a merge is allowed.</li>
  <li>The PR is blocked from merging until the finding is addressed or dismissed.</li>
</ol>

<p>See <a href="./configurations.html">Configure Repositories</a> for the full branch protection setup walkthrough.</p>

<h2 id="status-checks">Status Checks</h2>

<p>DryRun Security posts individual status checks for each enabled agent and code policy. This granularity lets you enforce specific security gates - for example, requiring the Secrets Analyzer to pass on all PRs to <code>main</code>, while treating other agent findings as advisory.</p>

<p>Available status checks include:</p>
<ul>
  <li><strong>Code Policies</strong> - A single aggregated check for all NLCP policy findings.</li>
  <li><strong>Individual agent checks</strong> - One check per enabled Code Security Agent (e.g., <code>Secrets Analyzer</code>, <code>SQL Injection Analyzer</code>).</li>
</ul>

<h2 id="api-triggered-scans">API-Triggered Scans</h2>

<p>For more advanced CI/CD use cases, the <a href="./api-guide.html">DryRun Simple API</a> allows you to trigger DeepScans programmatically, retrieve findings, and integrate security data into your existing pipeline tooling. This enables patterns like:</p>

<ul>
  <li>Triggering a DeepScan on merge to <code>main</code> and ingesting findings into your issue tracker</li>
  <li>Querying current findings as part of a deployment gate decision</li>
  <li>Exporting SBOM data as a pipeline artifact on each release build</li>
</ul>

<h2 id="gitlab-pipelines">GitLab Pipelines</h2>

<p>On GitLab, DryRun Security integrates with Merge Request pipelines. Analysis results are posted as Merge Request comments and pipeline status checks. The same blocking capability is available through GitLab's merge request approval rules, enabling you to require DryRun Security's checks to pass before a merge is allowed.</p>
''',
}


# -- AI Agent Security --

PAGES['securing-ai-code'] = {
    'title': 'Securing AI-Generated Code',
    'description': 'How DryRun Security handles the unique security challenges of AI-generated code from coding assistants.',
    'section': 'AI Agent Security',
    'content': '''
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

<h2 id="ai-coding-visibility">Organizational Visibility</h2>

<p>Beyond per-PR security analysis, DryRun Security provides visibility into AI coding activity across your organization - tracking where AI-generated code is being introduced and what security implications it carries. See <a href="./ai-coding-visibility.html">AI Coding Visibility</a> for details.</p>
''',
}

PAGES['malicious-agent-detection'] = {
    'title': 'Malicious Agent Detection',
    'description': 'DryRun Security detects malicious AI agent behaviors - identifying when AI agents attempt to introduce backdoors or malicious code patterns.',
    'section': 'AI Agent Security',
    'content': '''
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

<p>Malicious agent detection is one layer in a defense-in-depth approach to AI coding security. Combined with Natural Language Code Policies that enforce organizational coding standards, the Secrets Analyzer detecting credential introduction, and the code security knowledge graph tracking behavioral patterns over time, DryRun Security provides comprehensive coverage against AI-specific security risks in the development pipeline.</p>
''',
}

PAGES['ai-coding-visibility'] = {
    'title': 'AI Coding Visibility',
    'description': 'Track AI coding activity across your organization - understand what AI agents are changing and the security implications.',
    'section': 'AI Agent Security',
    'content': '''
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
  <li><strong>Supply chain transparency</strong> - AI-BOM generation (see <a href="../sbom-generation.html">SBOM Generation</a>) provides a formal record of AI involvement in software production for compliance purposes.</li>
  <li><strong>Policy enforcement</strong> - Natural Language Code Policies can be configured specifically for AI-generated code sections, enforcing stricter review criteria where AI involvement is detected.</li>
</ul>
''',
}


# -- API Reference --

PAGES['api-guide'] = {
    'title': 'API Usage Guide',
    'description': 'Programmatic access to DryRun Security findings, scans, configurations, and insights via the Simple API.',
    'section': 'API Reference',
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

<h3 id="getting-an-api-key">Getting an API Key</h3>

<p>Create and manage access keys at: <a href="https://app.dryrun.security/settings/access-keys" target="_blank" rel="noopener noreferrer">https://app.dryrun.security/settings/access-keys</a></p>

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

<pre><code>curl \\
  -H "Authorization: Bearer $DRYRUN_API_KEY" \\
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

<p><code>GET /v1/accounts/{account_id}/custom_policies</code> - List all Natural Language Code Policies for an account.</p>

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

PAGES['language-support'] = {
    'title': 'Language Support',
    'description': 'DryRun Security supports all major programming languages with AI-powered contextual analysis.',
    'section': 'API Reference',
    'content': '''
<h2 id="ai-powered-language-agnostic-analysis">AI-Powered, Language-Agnostic Analysis</h2>

<p>Unlike traditional SAST tools that require language-specific parsers and rule sets for each supported language, DryRun Security's AI-native architecture enables analysis across all major programming languages. The same contextual analysis capabilities - data flow tracing, business logic evaluation, cross-file analysis - apply regardless of the language in which the code is written.</p>

<p>This matters for polyglot codebases, where security tools that only cover a subset of languages create blind spots. DryRun Security provides consistent coverage across the full stack.</p>

<h2 id="supported-languages">Supported Languages</h2>

<p>DryRun Security supports analysis of the following languages:</p>

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th>Language</th>
      <th>Ecosystems / Frameworks</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Python</td><td>Django, Flask, FastAPI, SQLAlchemy, and others</td></tr>
    <tr><td>JavaScript / TypeScript</td><td>Node.js, Express, React, Next.js, Vue, Angular</td></tr>
    <tr><td>Java</td><td>Spring Boot, Hibernate, Jakarta EE</td></tr>
    <tr><td>Kotlin</td><td>Spring Boot, Android</td></tr>
    <tr><td>Ruby</td><td>Ruby on Rails, Sinatra</td></tr>
    <tr><td>Go</td><td>Standard library, Gin, Echo, GORM</td></tr>
    <tr><td>PHP</td><td>Laravel, Symfony, WordPress</td></tr>
    <tr><td>C#</td><td>.NET / ASP.NET Core, Entity Framework</td></tr>
    <tr><td>Rust</td><td>Actix, Axum, Tokio</td></tr>
    <tr><td>Swift</td><td>iOS / macOS applications</td></tr>
    <tr><td>C / C++</td><td>Systems, embedded, and native code</td></tr>
    <tr><td>Scala</td><td>Play Framework, Akka</td></tr>
    <tr><td>Infrastructure</td><td>Terraform, CloudFormation, Kubernetes, Helm, Docker</td></tr>
  </tbody>
</table>
</div>

<h2 id="dependency-ecosystems">Dependency Ecosystems</h2>

<p>DryRun Security's Software Composition Analysis covers dependency manifests and lock files for all major package managers:</p>

<ul>
  <li><strong>npm / yarn / pnpm</strong> (JavaScript / TypeScript)</li>
  <li><strong>pip / poetry / pipenv</strong> (Python)</li>
  <li><strong>bundler</strong> (Ruby)</li>
  <li><strong>maven / gradle</strong> (Java / Kotlin)</li>
  <li><strong>go modules</strong> (Go)</li>
  <li><strong>cargo</strong> (Rust)</li>
  <li><strong>nuget</strong> (.NET)</li>
  <li><strong>composer</strong> (PHP)</li>
</ul>

<h2 id="language-version-risk">Language Version Risk</h2>

<p>In addition to analyzing code within a language, DryRun Security's coverage includes detecting <strong>Language Version Risk</strong> - the use of outdated or unsupported language runtime versions that carry known vulnerabilities. This applies across all supported languages and is particularly important for long-lived production codebases that may not have had their runtime dependencies updated recently.</p>
''',
}


# ---------------------------------------------------------------------------
# Build all pages - flat ordered list for prev/next navigation
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
    parts.append('<div class="sidebar-header">')
    parts.append(f'<a href="{esc(asset_prefix)}index.html" class="sidebar-logo-link">')
    parts.append(f'<img src="{esc(asset_prefix)}assets/logo.svg" alt="DryRun Security" class="sidebar-logo">')
    parts.append('</a>')
    parts.append('</div>')
    parts.append('<div class="sidebar-nav">')
    for section in SECTIONS:
        parts.append(f'<div class="sidebar-section">')
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
          <img src="{asset_prefix}assets/logo.svg" alt="DryRun Security" class="logo">
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
            <img src="{asset_prefix}assets/logo.svg" alt="DryRun Security" class="footer-logo-img">
          </a>
          <div class="footer-badges">
            <span class="footer-badge"><span class="footer-badge-dot"></span>SOC2 Type II Certified</span>
            <span class="footer-badge"><span class="footer-badge-dot"></span>Black Hat USA 2024 Finalist</span>
            <span class="footer-badge"><span class="footer-badge-dot"></span>G2 High Performer &mdash; SAST Spring 2026</span>
          </div>
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


def render_doc_page(slug: str, page: dict, asset_prefix: str = '../') -> str:
    title = page['title']
    description = page['description']
    section_name = page.get('section', get_section_for_slug(slug))
    raw_content = page['content'].strip()
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
        <h1 class="page-heading">{esc(title)}</h1>
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
  <script src="{asset_prefix}app.js"></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Index page
# ---------------------------------------------------------------------------

SECTION_ICONS = {
    'Getting Started': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>',
    'Scanning': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>',
    'AI & Intelligence': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 2a4 4 0 014 4v1h2a2 2 0 012 2v8a2 2 0 01-2 2H6a2 2 0 01-2-2V9a2 2 0 012-2h2V6a4 4 0 014-4z"/></svg>',
    'Remediation': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    'Platform': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
    'Developer Tools': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M8 9l-3 3 3 3M16 9l3 3-3 3M12 5l-2 14"/></svg>',
    'AI Agent Security': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4l2 2"/></svg>',
    'API Reference': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V6a2 2 0 00-2-2z"/><path d="M8 9h8M8 13h5"/></svg>',
}

SECTION_DESCRIPTIONS = {
    'Getting Started': 'Install DryRun Security on GitHub or GitLab and get your first scan running.',
    'Scanning': 'How DryRun Security analyzes code - from PR reviews to full repository DeepScans.',
    'AI & Intelligence': 'The architecture, methodology, and intelligence capabilities behind DryRun Security.',
    'Remediation': 'Fix findings, verify remediations, and manage false positives with precision.',
    'Platform': 'Dashboard, risk register, configurations, notifications, and platform analytics.',
    'Developer Tools': 'IDE integrations, MCP, AGENTS.md, and CI/CD pipeline integration.',
    'AI Agent Security': 'Security for AI-generated code, malicious agent detection, and AI coding visibility.',
    'API Reference': 'Programmatic access to DryRun Security data and supported languages.',
}


def render_index_page() -> str:
    header = HEADER_HTML.replace('{asset_prefix}', './')
    footer = FOOTER_HTML.replace('{asset_prefix}', './')

    cards_html = []
    for section in SECTIONS:
        section_name = section['name']
        icon = SECTION_ICONS.get(section_name, '')
        section_desc = SECTION_DESCRIPTIONS.get(section_name, '')
        first_slug = section['pages'][0]
        first_page = PAGES.get(first_slug, {})

        links_html = []
        for slug in section['pages']:
            page = PAGES.get(slug, {})
            title = page.get('title', slug)
            links_html.append(
                f'<li><a href="./docs/{esc(slug)}.html">{esc(title)}</a></li>'
            )

        cards_html.append(f'''      <div class="index-card">
        <div class="index-card-icon">{icon}</div>
        <h2 class="index-card-title">{esc(section_name)}</h2>
        <p class="index-card-desc">{esc(section_desc)}</p>
        <ul class="index-card-links">
          {''.join(links_html)}
        </ul>
      </div>''')

    cards_joined = '\n'.join(cards_html)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DryRun Security Documentation</title>
  <meta name="description" content="DryRun Security documentation - learn how to install, configure, and use DryRun Security to protect your codebase.">
  <link rel="icon" href="./assets/favicon.ico" type="image/png">
  <link rel="apple-touch-icon" href="./assets/logo192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./style.css">
</head>
<body>
{header}
  <section class="docs-hero">
    <div class="docs-hero-inner">
      <p class="docs-hero-eyebrow">Documentation</p>
      <h1 class="docs-hero-title">DryRun Security Docs</h1>
      <p class="docs-hero-subtitle">Everything you need to install, configure, and get the most out of DryRun Security - the AI-native application security platform.</p>
      <div class="docs-hero-search">
        <svg class="docs-search-icon" viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true"><path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/></svg>
        <input type="text" id="docsSearch" placeholder="Search documentation..." autocomplete="off">
      </div>
    </div>
  </section>
  <section class="docs-quickstart">
    <div class="docs-quickstart-inner">
      <p class="docs-quickstart-label">Quick start</p>
      <div class="docs-quickstart-links">
        <a href="./docs/quick-start.html" class="docs-quickstart-link">
          <span class="docs-quickstart-arrow">→</span>
          Install for GitHub
        </a>
        <a href="./docs/quick-start-gitlab.html" class="docs-quickstart-link">
          <span class="docs-quickstart-arrow">→</span>
          Install for GitLab
        </a>
        <a href="./docs/sast-overview.html" class="docs-quickstart-link">
          <span class="docs-quickstart-arrow">→</span>
          How scanning works
        </a>
        <a href="./docs/natural-language-code-policies.html" class="docs-quickstart-link">
          <span class="docs-quickstart-arrow">→</span>
          Custom code policies
        </a>
      </div>
    </div>
  </section>
  <section class="index-cards-section">
    <div class="index-cards-inner">
{cards_joined}
    </div>
  </section>
{footer}
  <script src="./app.js"></script>
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
# Build entry point
# ---------------------------------------------------------------------------

def build(output_dir: str = None) -> None:
    if output_dir is None:
        output_dir = Path(__file__).parent
    else:
        output_dir = Path(output_dir)

    docs_dir = output_dir / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Generate doc pages
    for slug in ORDERED_PAGES:
        page = PAGES.get(slug)
        if page is None:
            print(f'WARNING: No content defined for slug: {slug}')
            continue
        html_content = render_doc_page(slug, page, asset_prefix='../')
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

    total = len(ORDERED_PAGES) + 3  # pages + index + sitemap + robots
    print(f'\nBuild complete: {total} files generated in {output_dir}')


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else None
    build(out)
