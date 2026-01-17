#!/usr/bin/env python3
"""
Aegean Tour Itinerary Solver - Optimized Version
Handles up to 250 customers efficiently with backtracking.
"""

import sys
from typing import List, Tuple, Set

def solve() -> None:
    # Read input
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                lines = [line.strip() for line in f]
        except:
            print("NO ITINERARY")
            return
    else:
        lines = [line.strip() for line in sys.stdin]
    
    if len(lines) < 2:
        print("NO ITINERARY")
        return
    
    try:
        H = int(lines[0])
        C = int(lines[1])
    except:
        print("NO ITINERARY")
        return
    
    # Parse customers with validation
    customers: List[List[Tuple[int, str]]] = []
    for i in range(C):
        if i + 2 >= len(lines):
            print("NO ITINERARY")
            return
        
        prefs = []
        seen_hops = set()
        airborne_count = 0
        
        for pair in lines[i + 2].split(', '):
            h_str, t = pair.split()
            h = int(h_str)
            
            # Validate hop
            if h < 0 or h >= H:
                print("NO ITINERARY")
                return
            
            # Validate transport
            if t not in ['airborne', 'by-sea']:
                print("NO ITINERARY")
                return
            
            # Check for duplicate hops for same customer
            if h in seen_hops:
                print("NO ITINERARY")
                return
            seen_hops.add(h)
            
            # Check airborne limit (max 1 per customer)
            if t == 'airborne':
                airborne_count += 1
                if airborne_count > 1:
                    print("NO ITINERARY")
                    return
            
            prefs.append((h, t))
        
        if not prefs:
            print("NO ITINERARY")
            return
        
        customers.append(prefs)
    
    # Preprocess: For each customer, track what would satisfy them
    # customer_sat[i] = {'airborne': set_of_hops, 'by-sea': set_of_hops}
    customer_sat = []
    for prefs in customers:
        sat = {'airborne': set(), 'by-sea': set()}
        for hop, transport in prefs:
            sat[transport].add(hop)
        customer_sat.append(sat)
    
    # Backtracking search with pruning
    assignment = ['by-sea'] * H  # Start with all by-sea (optimal)
    best_assignment = None
    best_airborne = H + 1  # Worse than possible
    
    def can_still_satisfy(hop_idx: int, satisfied: List[bool]) -> bool:
        """Check if all unsatisfied customers can still be satisfied."""
        for i, sat in enumerate(customer_sat):
            if satisfied[i]:
                continue
            
            # Customer i not satisfied yet
            # Check if they have any remaining hops that could satisfy them
            has_possible = False
            
            # Check by-sea options in remaining hops
            for h in sat['by-sea']:
                if h >= hop_idx:  # Not processed yet
                    has_possible = True
                    break
            
            if not has_possible:
                # Check airborne options
                for h in sat['airborne']:
                    if h >= hop_idx:
                        has_possible = True
                        break
            
            if not has_possible:
                return False
        return True
    
    def backtrack(hop_idx: int, airborne_count: int, satisfied: List[bool]) -> bool:
        nonlocal best_assignment, best_airborne
        
        # Prune 1: Already worse than best found
        if airborne_count >= best_airborne:
            return False
        
        # Prune 2: Check if all customers can still be satisfied
        if not can_still_satisfy(hop_idx, satisfied):
            return False
        
        # Base case: all hops assigned
        if hop_idx == H:
            # Verify all customers satisfied
            if all(satisfied):
                if airborne_count < best_airborne:
                    best_assignment = assignment.copy()
                    best_airborne = airborne_count
                return True
            return False
        
        # Try by-sea first (optimal choice)
        assignment[hop_idx] = 'by-sea'
        
        # Update which customers get satisfied
        new_satisfied = satisfied.copy()
        for i, sat in enumerate(customer_sat):
            if not new_satisfied[i] and hop_idx in sat['by-sea']:
                new_satisfied[i] = True
        
        if backtrack(hop_idx + 1, airborne_count, new_satisfied):
            return True
        
        # Try airborne
        assignment[hop_idx] = 'airborne'
        
        new_satisfied = satisfied.copy()
        for i, sat in enumerate(customer_sat):
            if not new_satisfied[i] and hop_idx in sat['airborne']:
                new_satisfied[i] = True
        
        if backtrack(hop_idx + 1, airborne_count + 1, new_satisfied):
            return True
        
        return False
    
    # Start backtracking
    initial_satisfied = [False] * C
    backtrack(0, 0, initial_satisfied)
    
    # Output
    if best_assignment is None:
        print("NO ITINERARY")
    else:
        result = ', '.join(f"{i} {best_assignment[i]}" for i in range(H))
        print(result)

if __name__ == "__main__":
    solve()
