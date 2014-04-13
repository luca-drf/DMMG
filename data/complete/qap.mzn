% Quadratic Assignment Problem:
% There are a set of n facilities and a set of n locations.
% For each pair of locations, a distance is specified and
% for each pair of facilities a weight or flow is specified
% (e.g., the amount of supplies transported between the two facilities).
% The problem is to assign all facilities to different locations
% with the goal of minimizing the sum of the distances multiplied by the corresponding flows.


include "globals.mzn"; 
int: nlocations = 3;
array[1..nlocations, 1..nlocations] of int: distances;
array[1..nlocations, 1..nlocations] of int: weight;
array[1..nlocations] of var 1..nlocations: x;

constraint alldifferent(x); 

var int: z = sum(i,j in 1..nlocations) (distances[x[i],x[j]] * weight[i, j]);

%solve minimize z;
solve satisfy;

%
% data
%

% From OPL, car dat (smallest instance)
weight =
  array2d(1..nlocations, 1..nlocations, 
    [
        0, 90, 10,
       90,  0,  0,
       10,  0,  0
    ]);
distances = 
  array2d(1..nlocations, 1..nlocations,
   [
    0, 36, 54, 
   36,  0, 73, 
   54, 73, 0 
    ]);