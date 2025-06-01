import cytoscape from 'cytoscape';

// Common types and interfaces
interface Point {
  x: number;
  y: number;
}

interface ControlPoint {
  weight: number;
  distance: number;
}

/**
 * Gets node positions from an edge
 */
function getNodePositions(edge: cytoscape.EdgeSingular): {
  sourcePos: Point;
  targetPos: Point;
} {
  const sourcePos = {
    x: edge.source().position('x'),
    y: edge.source().position('y')
  };
  const targetPos = {
    x: edge.target().position('x'),
    y: edge.target().position('y')
  };
  
  return { sourcePos, targetPos };
}

/**
 * Applies control point parameters to an edge
 */
function applyControlPoints(edge: cytoscape.EdgeSingular, sourcePoint: Point, targetPoint: Point): void {
  
  const paramsSource = computeControlPointFromGlobalCoordinate(edge, sourcePoint.x, sourcePoint.y);
  const paramsTarget = computeControlPointFromGlobalCoordinate(edge, targetPoint.x, targetPoint.y);
  
  const controlWeights = [paramsSource.weight, paramsTarget.weight];
  const controlPointDistances = [paramsSource.distance, paramsTarget.distance];
  
  edge.style('control-point-weights', controlWeights);
  edge.style('control-point-distances', controlPointDistances);
}

/**
 * Compute control point parameters from global coordinate for Cytoscape's unbundled-bezier curve style
 * This implementation allows for weights outside the [0,1] range to precisely position control points
 * @param edge The edge to compute control point for
 * @param globalX Global X coordinate of the desired control point
 * @param globalY Global Y coordinate of the desired control point
 * @returns Object containing weight and distance parameters for bezier curve
 */
export function computeControlPointFromGlobalCoordinate(
  edge: cytoscape.EdgeSingular,
  globalX: number,
  globalY: number
): ControlPoint {
  const { sourcePos, targetPos } = getNodePositions(edge);

  const dx = targetPos.x - sourcePos.x;
  const dy = targetPos.y - sourcePos.y;
  const length = Math.sqrt(dx * dx + dy * dy);

  // If edge has no length, return default values
  if (length === 0) {
    return { weight: 0.5, distance: 0 };
  }
  
  // 1. Calculate direct vectors for better geometric calculations
  const vectorSourceGlobal = { 
    x: globalX - sourcePos.x, 
    y: globalY - sourcePos.y 
  };
  
  // 2. Calculate the projection factor of the global point onto the edge line
  const edgeDotProduct = dx * vectorSourceGlobal.x + dy * vectorSourceGlobal.y;
  const edgeLengthSquared = dx * dx + dy * dy;
  const rawWeight = edgeDotProduct / edgeLengthSquared; // This can be < 0 or > 1
  
  // 3. Calculate the perpendicular component - find projected point on edge line
  const projectedX = sourcePos.x + rawWeight * dx;
  const projectedY = sourcePos.y + rawWeight * dy;
  
  // 4. Calculate the perpendicular unit vector
  const perpUnitX = -dy / length; // Perpendicular by rotating 90 degrees
  const perpUnitY = dx / length;
  
  // 5. Vector from projected point to global point
  const toGlobalX = globalX - projectedX;
  const toGlobalY = globalY - projectedY;
  
  // 6. Dot product with perpendicular vector gives signed distance
  const perpDistance = toGlobalX * perpUnitX + toGlobalY * perpUnitY;
  
  return { weight: rawWeight, distance: perpDistance };
}


/**
 * Styles edges connecting from stored procedures to create visually appealing curves.
 * Adapts the curve style based on the relative positions of nodes.
 * @param isDatamodel If false, uses round-taxi style (for stored procedures), otherwise uses bezier style
 */
export function edgeNormal(edge: cytoscape.EdgeSingular, isDatamodel:boolean = true): void {

  if (!isDatamodel) {
    edge.style(
    {
      'curve-style': 'round-taxi',
      'source-endpoint': 'outside-to-node',
      'target-endpoint': 'outside-to-node',
      'taxi-direction': 'horizontal'
    })
    return
  }

  let xOffset = 140;
  let xWidthProcentOffset = 53;
  const { sourcePos, targetPos } = getNodePositions(edge);

  const dx = targetPos.x - sourcePos.x;
  const dy = targetPos.y - sourcePos.y;
  const length = Math.sqrt(dx * dx + dy * dy);



  edge.style(
    {
      'curve-style': 'unbundled-bezier',
      'source-endpoint': `${xWidthProcentOffset}% 0%`,
      'target-endpoint': `${-xWidthProcentOffset}% 0%`,
      'taxi-direction': 'horizontal'
    })
  
  // Create control points
  const controlPoints = {
    source: { x: sourcePos.x + xOffset, y: sourcePos.y },
    target: { x: targetPos.x - xOffset, y: targetPos.y }
  };
  
  // Apply the control points to the edge
  applyControlPoints(edge, controlPoints.source, controlPoints.target);
}

