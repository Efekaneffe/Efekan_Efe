import copy

class InventoryManager:
    def __init__(self):
        # Cleaned up unnecessary init arguments to focus on the core inventory structures
        self.inventory = {}       # Maps item -> current stock amount
        self.history = {}         # Maps checkpoint_id -> deep copy of inventory state

    def update_stock(self, item: str, amount: int) -> None:
        """Adds or removes stock for an item."""
        current_stock = self.get_stock(item)
        new_stock = current_stock + amount
        
        if new_stock < 0:
            raise ValueError(f"Cannot update stock '{item}' by {amount}. Current stock is {current_stock}.")
        
        self.inventory[item] = new_stock

    def get_stock(self, item: str) -> int:
        """Returns the current stock of an item. Returns 0 if item never existed."""
        return self.inventory.get(item, 0)  # Added missing 'return'

    def create_checkpoint(self, checkpoint_id: int) -> None:
        """Saves the current state under a unique integer ID."""
        if checkpoint_id in self.history:
            raise ValueError(f"Checkpoint ID {checkpoint_id} already exists.")
        
        # Save a deep copy of the complete inventory state at this point in time
        self.history[checkpoint_id] = copy.deepcopy(self.inventory)

    def rollback(self, checkpoint_id: int) -> None:
        """Restores the inventory state to exactly how it was when this checkpoint was made."""
        if checkpoint_id not in self.history:
            raise ValueError(f"Checkpoint ID {checkpoint_id} does not exist.")
        
        # Restore the inventory state
        self.inventory = copy.deepcopy(self.history[checkpoint_id])
        
        # Delete/Invalidate all checkpoints created AFTER this checkpoint_id
        invalid_ids = [cid for cid in self.history if cid > checkpoint_id]
        for cid in invalid_ids:
            del self.history[cid]
            
                


# =====================================================================
# AUTOMATED TEST SUITE
# =====================================================================
def run_inventory_tests():
    print("Running Challenge 1 Tests...")
    mgr = InventoryManager()
    
    # Test 1: Basic Stock Operations
    mgr.update_stock("apples", 10)
    mgr.update_stock("bananas", 5)
    assert mgr.get_stock("apples") == 10
    assert mgr.get_stock("bananas") == 5
    
    # Test 2: Inventory Cannot Go Negative
    try:
        mgr.update_stock("apples", -15)
        print("❌ Test 2 Failed: Allowed negative stock!")
        return
    except ValueError:
        assert mgr.get_stock("apples") == 10, "Stock changed despite error!"
        
    # Test 3: Checkpoint and Basic Rollback
    mgr.create_checkpoint(101)
    mgr.update_stock("apples", 5)       # apples = 15
    mgr.update_stock("oranges", 20)     # oranges = 20
    
    mgr.create_checkpoint(102)
    mgr.update_stock("apples", -10)     # apples = 5
    mgr.update_stock("bananas", 10)     # bananas = 15
    
    # Check current state before rollback
    assert mgr.get_stock("apples") == 5
    assert mgr.get_stock("oranges") == 20
    assert mgr.get_stock("bananas") == 15
    
    # Rollback to checkpoint 102
    mgr.rollback(102)
    assert mgr.get_stock("apples") == 15
    assert mgr.get_stock("bananas") == 5
    assert mgr.get_stock("oranges") == 20
    print("✓ Passed basic rollback")

    # Test 4: Deep Rollback (Cascading deletion of future checkpoints)
    mgr.rollback(101)
    assert mgr.get_stock("apples") == 10
    assert mgr.get_stock("bananas") == 5
    assert mgr.get_stock("oranges") == 0
    
    # Checkpoint 102 should no longer exist because we rolled back past it
    try:
        mgr.rollback(102)
        print("❌ Test 4 Failed: Allowed rollback to a discarded future checkpoint!")
        return
    except ValueError:
        print("✓ Passed cascading checkpoint invalidation")
        
    print("🎉 ALL CHALLENGE 1 TESTS PASSED PERFECTLY! 🎉\n")

if __name__ == "__main__":
    run_inventory_tests()