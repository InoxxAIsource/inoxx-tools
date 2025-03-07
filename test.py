def test_function():
    # This is a test function
    pass

class DataProcessor:
    """A class for processing and transforming data"""

    def __init__(self, data=None):
        self.data = data or []
        self.processed = False

    def add_item(self, item):
        """Add an item to the data list

        Args:
            item: The item to add to the data collection
        """
        self.data.append(item)
        self.processed = False

    def process_data(self, transform_func=None):
        """Process the data using an optional transform function

        Args:
            transform_func (callable, optional): A function to transform each data item

        Returns:
            list: The processed data items
        """
        if transform_func:
            self.data = [transform_func(item) for item in self.data]
        self.processed = True
        return self.data

def calculate_average(numbers):
    """Calculate the average of a list of numbers

    Args:
        numbers (list): A list of numeric values

    Returns:
        float: The average of the input numbers

    Raises:
        ValueError: If the input list is empty
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)

# Example usage
if __name__ == "__main__":
    # Initialize processor with sample data
    processor = DataProcessor([1, 2, 3, 4, 5])

    # Define a transform function
    double = lambda x: x * 2

    # Process data and calculate average
    processed_data = processor.process_data(double)
    result = calculate_average(processed_data)
    print(f"Average of processed data: {result}")