import os
import time
import math
import random
from collections import Counter

# --- 1. Generator Implementations --- 

# 1.1 Linear Congruential Generator (LCG) 
class LCG: 
    def __init__(self, seed=None, a=1103515245, c=12345, m=2**31): 
        # Use a consistent seed for reproducibility across different runs/users 
        self.state = seed if seed is not None else 1234567 
        self.a = a 
        self.c = c 
        self.m = m 

    def next(self): 
        # LCG formula: X(n+1) = (a * X(n) + c) mod m 
        self.state = (self.a * self.state + self.c) % self.m 
        return self.state 

    def generate_byte(self): 
        # Return the least significant 8 bits of the 31-bit state 
        return self.next() & 0xFF 

    def generate_bytes(self, n):
        return bytes([self.generate_byte() for _ in range(n)])

# 1.2 Mersenne Twister (MT) 
class MersenneTwister: 
    def __init__(self, seed=None): 
        self.seed = seed if seed is not None else 1234567 
        self.rng = random.Random(self.seed) 

    def generate_byte(self): 
        # Returns a random integer in the range [0, 255] 
        return self.rng.randrange(256) 

    def generate_bytes(self, n):
        return self.rng.randbytes(n)

# 1.3 ChaCha20 (CSPRNG) - Cryptographically Secure 
try: 
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms 
    from cryptography.hazmat.backends import default_backend 

    class ChaCha20RNG: 
        def __init__(self): 
            # Key and Nonce setup using a deterministic process for testing consistency 
            seed_value = 1234567  
            
            # Key must be 32 bytes (256-bit) 
            self.key = seed_value.to_bytes(32, 'big') 
            # Nonce must be 16 bytes 
            self.nonce = (seed_value + 1).to_bytes(16, 'big') 
            
            self.cipher = Cipher(algorithms.ChaCha20(self.key, self.nonce), mode=None, backend=default_backend()) 
            self.encryptor = self.cipher.encryptor() 
            self.buffer = b'' 

        def generate_byte(self): 
            if not self.buffer: 
                # Generate a new block of keystream (64 bytes) 
                self.buffer += self.encryptor.update(b'\x00' * 64) 

            byte_value = self.buffer[0] 
            self.buffer = self.buffer[1:] 
            return byte_value 

        def generate_bytes(self, n):
            return self.encryptor.update(b'\x00' * n)

except ImportError: 
    # If cryptography is not installed, define a placeholder class 
    class ChaCha20RNG: 
        def __init__(self): 
            raise NotImplementedError("ChaCha20RNG requires the 'cryptography' library.") 

        def generate_byte(self): 
            raise NotImplementedError("ChaCha20RNG requires the 'cryptography' library.") 

        def generate_bytes(self, n):
            raise NotImplementedError("ChaCha20RNG requires the 'cryptography' library.")

# 1.4 Python's 'secrets' Module (CSPRNG) 
class SecretsRNG: 
    def generate_byte(self): 
        # Uses os.urandom 
        return os.urandom(1)[0]  

    def generate_bytes(self, n):
        return os.urandom(n)

# --- 2. Statistical Test Functions --- 

def shannon_entropy(data): 
    """Calculates Shannon Entropy (H) of a sequence of bytes (Ideal max 8.0).""" 
    if not data: return 0.0 
      
    byte_counts = Counter(data) 
    total_bytes = len(data) 
      
    entropy = 0.0 
    for count in byte_counts.values(): 
        probability = count / total_bytes 
        entropy -= probability * math.log2(probability) 
          
    return entropy 

def chi_square_test(data): 
    """Performs the Chi-Square Test for uniformity of byte distribution (Ideal 255.0).""" 
    if not data or len(data) < 256: return 0.0 

    total_bytes = len(data) 
    # Expected count for each byte value if uniform (E) 
    expected_count = total_bytes / 256.0 
      
    # Observed counts (O) 
    observed_counts = Counter(data) 
      
    chi_square_sum = 0.0 
      
    for i in range(256): 
        observed = observed_counts.get(i, 0) 
        chi_square_sum += (observed - expected_count)**2 / expected_count 
          
    return chi_square_sum 

# --- 3. Execution Framework --- 

def run_tests_and_measure(generator_instance, size_bits, runs=5): 
    """Generates the byte stream, runs tests, and measures generation time. 
       Takes size in BITS and converts to BYTES.""" 
      
    size_bytes = size_bits // 8 
      
    # --- Efficiency Measurement --- 
    times = [] 
      
    for _ in range(runs): 
        start_time = time.perf_counter() 
          
        if hasattr(generator_instance, 'generate_bytes'):
            byte_sequence = generator_instance.generate_bytes(size_bytes)
        else:
            byte_sequence = bytes([generator_instance.generate_byte() for _ in range(size_bytes)]) 
          
        end_time = time.perf_counter() 

        times.append(end_time - start_time) 

    mean_time = sum(times) / runs 
      
    # Calculate standard deviation 
    if runs > 1: 
        variance = sum([(t - mean_time) ** 2 for t in times]) / (runs - 1) 
        std_dev = math.sqrt(variance) 
    else: 
        std_dev = 0.0 

    # Use the last generated sequence for statistical tests 
    data = byte_sequence  
      
    # --- Statistical Tests --- 
    results = { 
        'generator': generator_instance.__class__.__name__, 
        'size_bits': size_bits, # Store size in bits 
        'mean_time_sec': mean_time, 
        'std_dev_sec': std_dev, 
        # Run live tests on the generated data 
        'shannon_entropy': shannon_entropy(data), 
        'chi_square': chi_square_test(data), 

        'raw_data': data 
    } 
      
    return results 

def save_bitstream_for_external_tests(data, generator_name, size_bits): 
    """Saves the raw bytes to a binary file for NIST input.""" 
    size_mbits = size_bits // 1_000_000 
    filename = f"bitstream_{generator_name}_{size_mbits}M_bits.bin" 
      
    os.makedirs('bitstreams', exist_ok=True) 
    filepath = os.path.join('bitstreams', filename) 
      
    try: 
        with open(filepath, 'wb') as f: 
            f.write(data) 
        return filepath 
    except Exception as e: 
        return f"Error saving file: {e}" 

# --- 4. Main Execution --- 

if __name__ == "__main__": 

    # Configuration 
    BITSTREAM_SIZES_BITS = [1_000_000, 5_000_000, 10_000_000]  
    NUM_RUNS_FOR_TIME_TEST = 5 # Number of times to run generation for time average 

    # List of generators to test 
    generators = { 
        "LCG": LCG(), 
        "MersenneTwister": MersenneTwister(), 
        "ChaCha20RNG": ChaCha20RNG() if 'ChaCha20RNG' in globals() and ChaCha20RNG.__name__ == 'ChaCha20RNG' else None, 
        "SecretsRNG": SecretsRNG() 
    } 

    print("--- RNG Statistical Testing Framework ---") 
    print("Generating and testing 1Mb, 5Mb, and 10Mb data streams.") 
    print("-" * 70) 
      
    all_results = [] 

    # Iterate through all generators 
    for gen_name, generator in generators.items(): 
        if generator is None: 
            continue 

        display_name = gen_name # Use the class name for display 
          
        print(f"\n[Testing Generator: {display_name}]") 
          
        # Iterate through all required bitstream sizes 
        for size in BITSTREAM_SIZES_BITS:  
            size_mbits = size // 1_000_000 
            print(f" > Running test for {size_mbits} Million bits...") 
              
            try: 
                # Run the tests and timing 
                results = run_tests_and_measure(generator, size, NUM_RUNS_FOR_TIME_TEST) 
                results['generator'] = display_name  
                all_results.append(results) 
                  
                # Save the raw data for external NIST/Correlation tests 
                filepath = save_bitstream_for_external_tests(results['raw_data'], gen_name, size) 
                  
                # Print summary 
                print(f"    - Mean Time: {results['mean_time_sec']:.6f}s (Std Dev: {results['std_dev_sec']:.6f}s)") 
                print(f"    - Shannon Entropy (Ideal 8.0): {results['shannon_entropy']:.4f}") 

                print(f"    - Chi-Square (Ideal 255.0): {results['chi_square']:.2f}") 
                print(f"    - Raw data saved to: {filepath}") 

            except NotImplementedError as e: 
                print(f"    [Error] Skipping {gen_name}: {e}") 
            except Exception as e: 
                print(f"    [CRITICAL ERROR] Failed to test {gen_name} at size {size} bits: {e}") 

    print("\n" + "=" * 70) 
    print("TESTING COMPLETE") 
    print("=" * 70) 
      
    print("\n--- Summary Table of Performance and Statistical Indicators ---") 
    print("-" * 104) 
    print("{:<20} {:<10} {:<15} {:<15} {:<15} {:<15}".format( 
        "Generator", "Size (Mb)", "Time (s)", "Std Dev (s)", "Shannon H", "Chi-Square" 
    )) 
    print("-" * 104) 
      
    for r in all_results: 
        size_mb_output = r['size_bits'] // 1_000_000 
          
        if r['mean_time_sec'] > 0: 
            print("{:<20} {:<10} {:<15.6f} {:<15.6f} {:<15.4f} {:<15.2f}".format( 
                r['generator'],  
                size_mb_output,  
                r['mean_time_sec'],  
                r['std_dev_sec'],  
                r['shannon_entropy'],  
                r['chi_square'] 
            )) 
        else: 
             print(f"{r['generator']:<20} {size_mb_output:<10} {'--- FAILED ---':<15} {'--- FAILED ---':<15} {'--- FAILED ---':<15} {'--- FAILED ---':<15}") 
              
    print("-" * 104) 
    print("\n* Raw binary files have been saved to the 'bitstreams' folder.") 
    print("Critical Chi-Square range : 99% confidence, df=255")