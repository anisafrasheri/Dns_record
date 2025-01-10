from flask import Flask, request, render_template, jsonify
import dns.resolver
import socket
import requests

app = Flask(__name__)

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Fetch DNS Records Route
@app.route("/get_dns_records", methods=["POST"])
def get_dns_records():
    website = request.json.get("website")
    dns_records = {}

    # DNS record types to fetch
    record_types = ['A', 'AAAA', 'MX', 'CNAME', 'NS', 'TXT', 'SOA']

    for record_type in record_types:
        try:
            records = dns.resolver.resolve(website, record_type)
            dns_records[record_type] = [record.to_text() for record in records]
        except dns.resolver.NoAnswer:
            dns_records[record_type] = ['No records found']
        except dns.resolver.NXDOMAIN:
            return jsonify({"error": f"The domain '{website}' does not exist."}), 404
        except Exception as e:
            dns_records[record_type] = [f"Error: {str(e)}"]

    return jsonify(dns_records)

# Reverse DNS Lookup
@app.route("/reverse_dns", methods=["POST"])
def reverse_dns():
    ip_address = request.json.get("ip")
    try:
        domain = socket.gethostbyaddr(ip_address)[0]
        return jsonify({"domain": domain})
    except Exception as e:
        return jsonify({"error": f"Error performing reverse DNS lookup: {str(e)}"}), 500

# Domain Health Checker
@app.route("/domain_health", methods=["POST"])
def domain_health():
    website = request.json.get("website")
    health_report = {}

    try:
        # Check if the domain resolves
        dns.resolver.resolve(website, 'A')
        health_report["DNS Resolution"] = "Domain resolves successfully."
    except Exception:
        health_report["DNS Resolution"] = "Domain does not resolve."

    # Blacklist check (Example using a free blacklist API)
    try:
        response = requests.get(f"https://api.abuseipdb.com/api/v2/check?domain={website}")
        if response.status_code == 200:
            data = response.json()
            health_report["Blacklist Status"] = "No issues found" if data['data']['isWhitelisted'] else "Blacklisted"
        else:
            health_report["Blacklist Status"] = "Unable to check blacklist status."
    except Exception as e:
        health_report["Blacklist Status"] = f"Error: {str(e)}"

    # DNSSEC check (Stubbed for simplicity)
    health_report["DNSSEC"] = "DNSSEC status not implemented yet."

    return jsonify(health_report)

# DNS Propagation Checker
@app.route("/dns_propagation", methods=["POST"])
def dns_propagation():
    website = request.json.get("website")
    dns_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]  # Example public DNS servers
    propagation_results = {}

    for dns_server in dns_servers:
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            records = resolver.resolve(website, 'A')
            propagation_results[dns_server] = [record.to_text() for record in records]
        except dns.resolver.NXDOMAIN:
            propagation_results[dns_server] = ["Domain does not exist."]
        except dns.resolver.NoAnswer:
            propagation_results[dns_server] = ["No DNS records found."]
        except Exception as e:
            propagation_results[dns_server] = [f"Error: {str(e)}"]

    return jsonify(propagation_results)

# Public API for Developers
@app.route("/api/dns_lookup", methods=["POST"])
def api_dns_lookup():
    website = request.json.get("website")
    dns_records = {}

    record_types = ['A', 'AAAA', 'MX', 'CNAME', 'NS', 'TXT', 'SOA']
    for record_type in record_types:
        try:
            records = dns.resolver.resolve(website, record_type)
            dns_records[record_type] = [record.to_text() for record in records]
        except Exception:
            dns_records[record_type] = ['No records found']

    return jsonify(dns_records)

if __name__ == "__main__":
    app.run(debug=True)
