% Bus driver scheduling problem (prob022 in CSPLib) in MiniZinc.

int: num_work;
int: num_shifts;
int: min_num_shifts;
array[1..num_shifts] of set of int: shifts;

array[1..num_shifts] of var 0..1: x;
var min_num_shifts..num_shifts: tot_shifts = sum(x);

% solve :: int_search(
%         x ++ [tot_shifts], 
%         first_fail, 
%         indomain_min, 
%         complete) 
%     minimize tot_shifts;
% 
% constraint
%    forall(j in 0..num_work-1) (
%        sum(i in 1..num_shifts where j in shifts[i])( x[i] ) = 1
%    );
% 
% output [
%   "num_shifts: " ++ show(num_shifts) ++ "\\n" ++ 
%   "x: " ++ show(x) ++ "\\n"
% ] ++ 
% [
%   ( if fix(x[i]) = 1 then show(shifts[i]) else "" endif ) 
%   | i in 1..num_shifts
% ] ++ ["\\n"];
