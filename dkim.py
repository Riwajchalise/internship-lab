import dns.resolver

def get_dkim_record(domain, selector="google"):
    try:
        dkim_domain = f"{selector}._domainkey.{domain}"
        print(f"🔍 Looking up DKIM for: {dkim_domain}")
        
        answers = dns.resolver.resolve(dkim_domain, 'TXT')
        for rdata in answers:
            # Join fragments and decode
            txt_record = ''.join([part.decode() if isinstance(part, bytes) else part for part in rdata.strings])
            print("\n✅ DKIM TXT Record:")
            print(txt_record)
            return txt_record
    except Exception as e:
        print(f"❌ Failed to fetch DKIM for {domain}: {e}")
        return None

# Replace with your domain
domain = "sentry.cy"
get_dkim_record(domain)
