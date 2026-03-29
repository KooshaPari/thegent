package byteport

import "context"

// DetectAppType auto-detects application type
func (c *Client) DetectAppType(ctx context.Context, req *DetectRequest) (*DetectResponse, error) {
	var detect DetectResponse
	if err := c.doRequest(ctx, "POST", "/detect", req, &detect); err != nil {
		return nil, err
	}
	return &detect, nil
}

// EstimateCost estimates deployment cost
func (c *Client) EstimateCost(ctx context.Context, req *EstimateCostRequest) (*EstimateCostResponse, error) {
	var estimate EstimateCostResponse
	if err := c.doRequest(ctx, "POST", "/estimate-cost", req, &estimate); err != nil {
		return nil, err
	}
	return &estimate, nil
}
