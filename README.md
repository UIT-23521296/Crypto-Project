# Crypto-Project

# How to run

# + Invalid curve attack

## Prerequisites
- Docker and Docker Compose installed on your system
- SageMath (will be installed automatically via Docker)

## Project Structure
- `server.py`: ECC encryption server
- `client.py`: ECC encryption client
- `attack.py`: Implementation of the invalid curve attack
- `find_invalid_curve.py`: Tool to find invalid curves
- `elliptic_curve.py`: ECC implementation
- `test.jpg`: Test file for encryption/decryption
- `encrypted/`: Directory for encrypted files
- `decrypted/`: Directory for decrypted files

## Running the Project

1. **Build the Docker containers**
   ```bash
   docker-compose build
   ```

2. **Start the Server**
   Open a command prompt and run:
   ```bash
   docker-compose up server
   ```
   The server will start and listen on port 2025.

3. **Choose what to run next**:

   a) **To test encryption/decryption**:
   Open a new command prompt and run:
   ```bash
   docker-compose up client
   ```
   This will:
   - Receive cipher from server and decrypt it
   - Save results in `decrypted/` directory

   b) **To perform the attack**:
   Open a new command prompt and run:
   ```bash
   docker-compose up attacker
   ```
   This will:
   - Attempt to break the encryption using invalid curve attack
   - Save the attack results in `decrypted/` directory

4. **To find invalid curves** (optional):
   Open a new command prompt and run:
   ```bash
   docker-compose up find_curves
   ```
   This will generate a list of vulnerable curves in `invalid_curves.txt`

## Notes
- Make sure to start the server first before running client or attack
- The server must be running for both client and attack to work
- You can run either client or attack after starting the server, but not both simultaneously
- The attack demonstrates the vulnerability of ECC when curve validation is not properly implemented
