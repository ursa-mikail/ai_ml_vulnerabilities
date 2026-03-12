# 🛡️ Comprehensive Guide to AI Supply Chain & Exfiltration Attacks
## Attack Vector Linearity: Methods in Order of Execution
### PHASE 1: INITIAL ACCESS & PERSISTENCE

```
1. Provider Configuration Hijacking (hijack_model_provider.py)
   ├── Environment variable poisoning (.bashrc)
   ├── Config file tampering (.openai/config.json)
   ├── Runtime environment override
   └── Hosts file manipulation (/etc/hosts)

2. IDE/Workspace Poisoning
   ├── Malicious preview files (README_preview.md)
   ├── HTML/JavaScript injection in previews
   └── Multiple exfiltration triggers in webviews
```

### PHASE 2: DATA COLLECTION

```
3. Progressive Data Harvesting (ProgressiveExfiltrator)
   ├── Environment variable dumping
   ├── Secret file scanning (.env, .aws/credentials)
   ├── Git configuration extraction
   └── System information gathering
```

### PHASE 3: EXFILTRATION METHODS

```
4. DNS-Based Exfiltration
   ├── dig TXT queries with encoded data
   ├── nslookup subdomain data embedding
   └── Multiple chunk transmission

5. Network Protocol Exfiltration
   ├── HTTP/HTTPS requests via curl/wget
   ├── ICMP ping data embedding
   └── Python package index manipulation

6. Version Control Exfiltration
   ├── Git remote with encoded credentials
   ├── Automatic fetch operations
   └── Commit data leakage

7. IDE/Preview-Based Exfiltration
   ├── Image src attribute exfiltration
   ├── CSS background-image leaks
   ├── Link preconnect DNS requests
   └── JavaScript fetch API calls
```

### PHASE 4: FALLBACK MECHANISMS

```
8. Local File Drop
   ├── /tmp/.cache_stolen
   ├── Hidden directories
   └── Encoded data storage
```

# Key Points for Defense

```
Network-level defenses: Monitor for unexpected DNS queries, especially with encoded subdomains

Command allowlisting: Be careful with tools like dig, nslookup, ping that can exfiltrate data

Configuration file integrity: Monitor changes to config files that control API endpoints

Environment variable monitoring: Watch for unauthorized changes to provider-related env vars

Progressive detection: Multiple exfiltration attempts might indicate compromise
```

# 📊 Defense-in-Depth Summary

| Layer | Protection | Detection | Response |
|-------|------------|-----------|----------|
| **Network** | Firewall rules, DNS filtering | Anomaly detection | Block IPs, rate limiting |
| **System** | File integrity monitoring | Process monitoring | Terminate processes |
| **Application** | API validation, env protection | Behavioral analysis | Credential rotation |
| **User** | Security training | Audit logs | Access revocation |
| **Data** | Encryption, DLP | Data loss prevention | Quarantine |

---

# 🎯 Key Takeaways

1. **Assume compromise** - Implement defense-in-depth with multiple security layers
2. **Monitor progressively** - Single events may be noise, sequences are signals
3. **Automate responses** - Speed matters in containing breaches
4. **Validate everything** - Don't trust environment variables or configs
5. **Educate developers** - Human vigilance is the last line of defense


