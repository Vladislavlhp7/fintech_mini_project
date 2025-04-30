from yield_utils import simulation

def main():
    """
    Main function to run the simulation.
    """
    result = simulation()
    print(f"Simulation completed with hit rate: {result['hit_rate']:.2%}")
    print("Simulation data:")
    print(result['data'].head())

if __name__ == "__main__":
    main()
