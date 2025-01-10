from flask import Flask, request, render_template, jsonify
import dns.resolver
import socket
import re
import requests
import whois
import ssl
from datetime import datetime

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
    website_or_ip = request.json.get("website")  # Accept either domain or IP

    if is_valid_ip(website_or_ip):
        try:
            domain = socket.gethostbyaddr(website_or_ip)[0]
            return jsonify({"domain": domain})
        except socket.herror:
            return jsonify({"error": f"Reverse DNS lookup failed for IP: {website_or_ip}"}), 500
    else:
        return jsonify({"error": f"Provided input '{website_or_ip}' is not a valid IP address for reverse lookup"}), 400

# Function to validate IP address
def is_valid_ip(ip):
    regex = r'^(\d{1,3}\.){3}\d{1,3}$'
    return re.match(regex, ip) is not None

# Domain Health Checker with Blacklist Check
@app.route("/domain_health", methods=["POST"])
def domain_health():
    website = request.json.get("website")
    health_report = {}

    try:
        dns.resolver.resolve(website, 'A')
        health_report["DNS Resolution"] = "Domain resolves successfully."
    except Exception:
        health_report["DNS Resolution"] = "Domain does not resolve."

    try:
        response = requests.get(f"https://api.abuseipdb.com/api/v2/check?domain={website}",
                                headers={"Key": "YOUR_API_KEY"})  # Replace with your actual API key
        if response.status_code == 200:
            data = response.json()
            health_report["Blacklist Status"] = "No issues found" if data['data']['isWhitelisted'] else "Blacklisted"
        else:
            health_report["Blacklist Status"] = "Unable to check blacklist status."
    except Exception as e:
        health_report["Blacklist Status"] = f"Error: {str(e)}"

    health_report["DNSSEC"] = "DNSSEC status not implemented yet."

    return jsonify(health_report)

# DNS Propagation Checker
@app.route("/dns_propagation", methods=["POST"])
def dns_propagation():
    website = request.json.get("website")
    dns_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]
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

# Blacklist Check (Additional Endpoint)
@app.route("/blacklist_check", methods=["POST"])
def blacklist_check():
    website = request.json.get("website")
    blacklist_report = {}

    try:
        response = requests.get(f"https://api.abuseipdb.com/api/v2/check?domain={website}",
                                headers={"Key": "YOUR_API_KEY"})  # Replace with your actual API key
        if response.status_code == 200:
            data = response.json()
            blacklist_report["Blacklist Status"] = "No issues found" if data['data']['isWhitelisted'] else "Blacklisted"
        else:
            blacklist_report["Blacklist Status"] = "Unable to check blacklist status."
    except Exception as e:
        blacklist_report["Blacklist Status"] = f"Error: {str(e)}"

    return jsonify(blacklist_report)

# WHOIS Lookup
@app.route("/whois_lookup", methods=["POST"])
def whois_lookup():
    domain = request.json.get("domain")
    try:
        domain_info = whois.whois(domain)
        return jsonify(domain_info)
    except Exception as e:
        return jsonify({"error": f"Error fetching WHOIS data: {str(e)}"}), 500

# SSL/TLS Certificate Check
@app.route("/ssl_check", methods=["POST"])
def ssl_check():
    domain = request.json.get("domain")
    try:
        conn = ssl.create_default_context().wrap_socket(socket.socket(), server_hostname=domain)
        conn.connect((domain, 443))
        cert = conn.getpeercert()
        expiry_date = cert['notAfter']
        expiry_date = datetime.strptime(expiry_date, '%b %d %H:%M:%S %Y GMT')
        return jsonify({"SSL Expiry Date": expiry_date.strftime("%Y-%m-%d")})
    except Exception as e:
        return jsonify({"error": f"SSL Check failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
