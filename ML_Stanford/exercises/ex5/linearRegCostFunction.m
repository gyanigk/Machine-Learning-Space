function [J, grad] = linearRegCostFunction(X, y, theta, lambda)
%LINEARREGCOSTFUNCTION Compute cost and gradient for regularized linear 
%regression with multiple variables
%   [J, grad] = LINEARREGCOSTFUNCTION(X, y, theta, lambda) computes the 
%   cost of using theta as the parameter for linear regression to fit the 
%   data points in X and y. Returns the cost in J and the gradient in grad

% Initialize some useful values
m = length(y); % number of training examples

% You need to return the following variables correctly 
J = 0;
grad = zeros(size(theta));

% ====================== YOUR CODE HERE ======================
% Instructions: Compute the cost and gradient of regularized linear 
%               regression for a particular choice of theta.
%
%               You should set J to the cost and grad to the gradient.
%

%h = X* theta;
%J = cost(i)
%J = 1/(2*m) * (h - y)' * (h - y) + (lambda/(2*m)) * (theta(2:length(theta)))' * theta(2:length(theta));
%thetaZero = theta;
%thetaZero(1) = 0;
%gradient formula
%grad = ((1 / m) * (h - y)' * X) + lambda / m * thetaZero';
A = X';
J = ((1/(2 * m)) * (sum(((X*theta) - y).^2))) + ((lambda / (2 * m)) * (sum( (theta(2:end,1)).^2 )));
grad = ((1/m)*(X' * ((X*theta) - y))) + ((lambda/m) * theta);
grad(1,1) = ((1/m) * (A(1,:) * ((X*theta) - y)));

% =========================================================================
grad = grad(:);

end
