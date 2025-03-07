"""
Graph Neural Network for Chess Position Understanding

This implementation creates a GNN model that represents a chess position as a graph,
where pieces are nodes and their relationships (attacking, defending, etc.) are edges.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import chess
from typing import Dict, List, Tuple, Optional, Any

class ChessPieceEncoder(nn.Module):
    """Encoder for chess pieces into feature vectors."""
    
    def __init__(self, embedding_dim: int = 32):
        """Initialize the piece encoder.
        
        Args:
            embedding_dim: Dimension of piece embeddings
        """
        super().__init__()
        
        # 12 piece types (6 types * 2 colors) + 1 for empty squares
        self.piece_embedding = nn.Embedding(13, embedding_dim)
        
        # Position encoder (for square location)
        self.rank_embedding = nn.Embedding(8, embedding_dim // 4)
        self.file_embedding = nn.Embedding(8, embedding_dim // 4)
        
        # Combine embeddings
        self.combiner = nn.Sequential(
            nn.Linear(embedding_dim + embedding_dim // 2, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
    
    def forward(self, piece_ids: torch.Tensor, ranks: torch.Tensor, files: torch.Tensor) -> torch.Tensor:
        """Forward pass to embed pieces with their positions.
        
        Args:
            piece_ids: Tensor of piece type IDs [batch_size, num_pieces]
            ranks: Tensor of rank indices [batch_size, num_pieces]
            files: Tensor of file indices [batch_size, num_pieces]
            
        Returns:
            Tensor of piece embeddings [batch_size, num_pieces, embedding_dim]
        """
        # Embed pieces
        piece_embeds = self.piece_embedding(piece_ids)  # [batch, pieces, dim]
        
        # Embed positions
        rank_embeds = self.rank_embedding(ranks)  # [batch, pieces, dim/4]
        file_embeds = self.file_embedding(files)  # [batch, pieces, dim/4]
        
        # Concatenate position embeddings
        pos_embeds = torch.cat([rank_embeds, file_embeds], dim=-1)  # [batch, pieces, dim/2]
        
        # Combine piece and position embeddings
        combined = torch.cat([piece_embeds, pos_embeds], dim=-1)  # [batch, pieces, dim + dim/2]
        node_embeds = self.combiner(combined)  # [batch, pieces, dim]
        
        return node_embeds


class ChessRelationEncoder(nn.Module):
    """Encoder for relationships between chess pieces."""
    
    def __init__(self, num_relations: int = 5, embedding_dim: int = 32):
        """Initialize the relation encoder.
        
        Args:
            num_relations: Number of relationship types
            embedding_dim: Dimension of relation embeddings
        """
        super().__init__()
        
        # Relation types: attacking, defending, controlling, threatened_by, blocking
        self.relation_embedding = nn.Embedding(num_relations, embedding_dim)
    
    def forward(self, relation_ids: torch.Tensor) -> torch.Tensor:
        """Forward pass to embed relations.
        
        Args:
            relation_ids: Tensor of relation type IDs [batch_size, num_edges]
            
        Returns:
            Tensor of relation embeddings [batch_size, num_edges, embedding_dim]
        """
        return self.relation_embedding(relation_ids)


class ChessGraphNeuralNetwork(nn.Module):
    """Graph Neural Network for chess positions."""
    
    def __init__(self, 
                 node_dim: int = 32, 
                 edge_dim: int = 32, 
                 hidden_dim: int = 64, 
                 num_layers: int = 3):
        """Initialize the chess GNN.
        
        Args:
            node_dim: Dimension of node features
            edge_dim: Dimension of edge features
            hidden_dim: Dimension of hidden layers
            num_layers: Number of GNN layers
        """
        super().__init__()
        
        self.node_dim = node_dim
        self.edge_dim = edge_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # Node and edge encoders
        self.node_encoder = ChessPieceEncoder(embedding_dim=node_dim)
        self.edge_encoder = ChessRelationEncoder(embedding_dim=edge_dim)
        
        # GNN layers
        self.gnn_layers = nn.ModuleList([
            GNNLayer(node_dim, edge_dim, hidden_dim)
            for _ in range(num_layers)
        ])
        
        # Output layers
        self.global_pool = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Position evaluation head
        self.eval_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)  # Single scalar output for evaluation
        )
        
        # Feature detection head
        self.feature_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 32)  # 32 binary features
        )
    
    def forward(self, batch: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        """Forward pass through the GNN.
        
        Args:
            batch: Dictionary containing:
                - node_ids: Piece IDs [batch_size, num_nodes]
                - ranks: Rank indices [batch_size, num_nodes]
                - files: File indices [batch_size, num_nodes]
                - edge_index: Edge connections [2, num_edges]
                - edge_type: Edge types [num_edges]
                - batch_idx: Batch indices for nodes [num_nodes]
            
        Returns:
            Dictionary with model outputs:
                - evaluation: Position evaluation [batch_size, 1]
                - features: Binary features [batch_size, 32]
        """
        # Encode nodes
        node_features = self.node_encoder(
            batch['node_ids'], 
            batch['ranks'], 
            batch['files']
        )  # [batch_size * num_nodes, node_dim]
        
        # Encode edges
        edge_features = self.edge_encoder(batch['edge_type'])  # [num_edges, edge_dim]
        
        # Run through GNN layers
        for layer in self.gnn_layers:
            node_features = layer(
                node_features, 
                batch['edge_index'], 
                edge_features
            )
        
        # Global pooling (aggregate node features for each graph in batch)
        pooled = self._global_pooling(node_features, batch['batch_idx'])
        pooled = self.global_pool(pooled)  # [batch_size, hidden_dim]
        
        # Compute outputs
        evaluation = self.eval_head(pooled)  # [batch_size, 1]
        features = self.feature_head(pooled)  # [batch_size, 32]
        
        return {
            'evaluation': evaluation,
            'features': features
        }
    
    def _global_pooling(self, node_features: torch.Tensor, batch_idx: torch.Tensor) -> torch.Tensor:
        """Perform global mean pooling.
        
        Args:
            node_features: Node features [num_nodes, node_dim]
            batch_idx: Batch indices for nodes [num_nodes]
            
        Returns:
            Pooled features [batch_size, node_dim]
        """
        num_graphs = batch_idx.max().item() + 1
        pooled = torch.zeros(num_graphs, node_features.shape[1], device=node_features.device)
        
        # Mean pooling
        for i in range(num_graphs):
            mask = (batch_idx == i)
            pooled[i] = node_features[mask].mean(dim=0)
        
        return pooled


class GNNLayer(nn.Module):
    """Graph Neural Network layer with edge features."""
    
    def __init__(self, node_dim: int, edge_dim: int, hidden_dim: int):
        """Initialize the GNN layer.
        
        Args:
            node_dim: Dimension of node features
            edge_dim: Dimension of edge features
            hidden_dim: Dimension of hidden layers
        """
        super().__init__()
        
        # Node feature transformation
        self.node_transform = nn.Sequential(
            nn.Linear(node_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_dim)
        )
        
        # Edge-conditioned message passing
        self.message_mlp = nn.Sequential(
            nn.Linear(node_dim + edge_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_dim)
        )
        
        # Update function
        self.update_mlp = nn.Sequential(
            nn.Linear(node_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, node_dim)
        )
        
        # Layer normalization
        self.layer_norm = nn.LayerNorm(node_dim)
    
    def forward(self, 
                node_features: torch.Tensor, 
                edge_index: torch.Tensor, 
                edge_features: torch.Tensor) -> torch.Tensor:
        """Forward pass through the GNN layer.
        
        Args:
            node_features: Node features [num_nodes, node_dim]
            edge_index: Edge connections [2, num_edges]
            edge_features: Edge features [num_edges, edge_dim]
            
        Returns:
            Updated node features [num_nodes, node_dim]
        """
        # Transform node features
        transformed_nodes = self.node_transform(node_features)
        
        # Compute messages
        source_nodes = edge_index[0]
        target_nodes = edge_index[1]
        
        # Get source node features for each edge
        source_features = node_features[source_nodes]  # [num_edges, node_dim]
        
        # Concatenate with edge features
        message_inputs = torch.cat([source_features, edge_features], dim=1)  # [num_edges, node_dim + edge_dim]
        
        # Compute messages
        messages = self.message_mlp(message_inputs)  # [num_edges, node_dim]
        
        # Aggregate messages (sum)
        aggregated = torch.zeros_like(node_features)
        aggregated.index_add_(0, target_nodes, messages)
        
        # Update node features
        update_inputs = torch.cat([node_features, aggregated], dim=1)  # [num_nodes, node_dim * 2]
        updates = self.update_mlp(update_inputs)  # [num_nodes, node_dim]
        
        # Residual connection and normalization
        outputs = self.layer_norm(node_features + updates)
        
        return outputs


class ChessPositionConverter:
    """Convert chess positions to graph representations for the GNN."""
    
    def __init__(self):
        """Initialize the converter."""
        # Map pieces to IDs
        self.piece_to_id = {
            'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,  # White pieces
            'p': 7, 'n': 8, 'b': 9, 'r': 10, 'q': 11, 'k': 12,  # Black pieces
            None: 0  # Empty square
        }
        
        # Map relation types to IDs
        self.relation_types = {
            'attacking': 0,
            'defending': 1,
            'controlling': 2,
            'threatened_by': 3,
            'blocking': 4
        }
    
    def board_to_graph(self, board: chess.Board) -> Dict[str, Any]:
        """Convert a chess board to graph representation.
        
        Args:
            board: Chess board
            
        Returns:
            Dictionary with graph data:
                - node_ids: Piece IDs for each node
                - ranks: Rank for each node
                - files: File for each node
                - edge_index: Edge connections
                - edge_type: Edge types
        """
        # Extract pieces and positions
        node_ids = []
        ranks = []
        files = []
        node_squares = []  # Keep track of square index for each node
        
        # Add nodes for pieces on the board
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                node_ids.append(self.piece_to_id[piece.symbol()])
                rank = chess.square_rank(square)
                file = chess.square_file(square)
                ranks.append(rank)
                files.append(file)
                node_squares.append(square)
        
        # Create edges for piece relationships
        edge_indices = [[], []]  # [source_nodes, target_nodes]
        edge_types = []
        
        # Number of nodes (pieces)
        num_nodes = len(node_ids)
        
        # Map from square index to node index
        square_to_node = {square: i for i, square in enumerate(node_squares)}
        
        # For each piece, find its relationships with other pieces
        for source_idx, source_square in enumerate(node_squares):
            piece = board.piece_at(source_square)
            piece_color = piece.color
            
            # Find attacks
            for attack_square in board.attacks(source_square):
                if attack_square in square_to_node:
                    target_idx = square_to_node[attack_square]
                    target_piece = board.piece_at(attack_square)
                    
                    if target_piece.color != piece_color:
                        # This piece is attacking an opponent's piece
                        edge_indices[0].append(source_idx)
                        edge_indices[1].append(target_idx)
                        edge_types.append(self.relation_types['attacking'])
                        
                        # The opponent's piece is threatened by this piece
                        edge_indices[0].append(target_idx)
                        edge_indices[1].append(source_idx)
                        edge_types.append(self.relation_types['threatened_by'])
                    else:
                        # This piece is defending a friendly piece
                        edge_indices[0].append(source_idx)
                        edge_indices[1].append(target_idx)
                        edge_types.append(self.relation_types['defending'])
            
            # Find controlled squares (potential future attacks)
            for target_square in chess.SQUARES:
                if target_square not in square_to_node and board.is_attacked_by(piece_color, target_square):
                    # Check if this specific piece attacks the square
                    moved_piece = chess.Move(source_square, target_square)
                    if board.is_pseudo_legal(moved_piece):
                        # Add a virtual node for the controlled square
                        node_ids.append(0)  # Empty square
                        ranks.append(chess.square_rank(target_square))
                        files.append(chess.square_file(target_square))
                        node_squares.append(target_square)
                        
                        target_idx = num_nodes
                        num_nodes += 1
                        square_to_node[target_square] = target_idx
                        
                        # This piece controls the empty square
                        edge_indices[0].append(source_idx)
                        edge_indices[1].append(target_idx)
                        edge_types.append(self.relation_types['controlling'])
            
            # Find blocking relationships
            if piece.piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                # Simulate removing the piece
                temp_board = board.copy()
                temp_board.remove_piece_at(source_square)
                
                # For each other piece of the same color
                for other_idx, other_square in enumerate(node_squares):
                    if other_idx == source_idx:
                        continue
                    
                    other_piece = board.piece_at(other_square)
                    if other_piece and other_piece.color == piece_color:
                        # Check if removing this piece changes attack patterns
                        before = set(board.attacks(other_square))
                        after = set(temp_board.attacks(other_square))
                        
                        if before != after:
                            # This piece is blocking the other piece
                            edge_indices[0].append(source_idx)
                            edge_indices[1].append(other_idx)
                            edge_types.append(self.relation_types['blocking'])
        
        # Convert to tensors
        graph_data = {
            'node_ids': torch.tensor(node_ids, dtype=torch.long),
            'ranks': torch.tensor(ranks, dtype=torch.long),
            'files': torch.tensor(files, dtype=torch.long),
            'edge_index': torch.tensor(edge_indices, dtype=torch.long),
            'edge_type': torch.tensor(edge_types, dtype=torch.long)
        }
        
        return graph_data
    
    def collate_graphs(self, graphs: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
        """Collate multiple graphs into a batch.
        
        Args:
            graphs: List of graph data dictionaries
            
        Returns:
            Batched graph data
        """
        batch_node_ids = []
        batch_ranks = []
        batch_files = []
        batch_edge_index = []
        batch_edge_type = []
        batch_idx = []
        
        node_offset = 0
        
        for i, graph in enumerate(graphs):
            num_nodes = graph['node_ids'].shape[0]
            
            batch_node_ids.append(graph['node_ids'])
            batch_ranks.append(graph['ranks'])
            batch_files.append(graph['files'])
            
            # Adjust edge indices
            edge_index = graph['edge_index'].clone()
            edge_index += node_offset
            batch_edge_index.append(edge_index)
            
            batch_edge_type.append(graph['edge_type'])
            batch_idx.extend([i] * num_nodes)
            
            node_offset += num_nodes
        
        # Concatenate
        return {
            'node_ids': torch.cat(batch_node_ids),
            'ranks': torch.cat(batch_ranks),
            'files': torch.cat(batch_files),
            'edge_index': torch.cat(batch_edge_index, dim=1),
            'edge_type': torch.cat(batch_edge_type),
            'batch_idx': torch.tensor(batch_idx, dtype=torch.long)
        }


# Training and evaluation functions

def train_gnn_model(model, train_loader, optimizer, device):
    """Train the GNN model for one epoch.
    
    Args:
        model: GNN model
        train_loader: DataLoader with training data
        optimizer: Optimizer
        device: Device to run on
        
    Returns:
        Average loss
    """
    model.train()
    total_loss = 0
    
    for batch in train_loader:
        # Move batch to device
        batch = {k: v.to(device) for k, v in batch.items() if isinstance(v, torch.Tensor)}
        target_eval = batch.pop('target_eval', None)
        target_features = batch.pop('target_features', None)
        
        # Forward pass
        outputs = model(batch)
        
        # Compute loss
        eval_loss = F.mse_loss(outputs['evaluation'], target_eval)
        feat_loss = F.binary_cross_entropy_with_logits(outputs['features'], target_features)
        loss = eval_loss + 0.1 * feat_loss
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(train_loader)


def evaluate_gnn_model(model, val_loader, device):
    """Evaluate the GNN model.
    
    Args:
        model: GNN model
        val_loader: DataLoader with validation data
        device: Device to run on
        
    Returns:
        Dictionary with metrics
    """
    model.eval()
    total_eval_loss = 0
    total_feat_loss = 0
    eval_corr = 0
    feat_accuracy = 0
    
    with torch.no_grad():
        for batch in val_loader:
            # Move batch to device
            batch = {k: v.to(device) for k, v in batch.items() if isinstance(v, torch.Tensor)}
            target_eval = batch.pop('target_eval')
            target_features = batch.pop('target_features')
            
            # Forward pass
            outputs = model(batch)
            
            # Compute losses
            eval_loss = F.mse_loss(outputs['evaluation'], target_eval)
            feat_loss = F.binary_cross_entropy_with_logits(outputs['features'], target_features)
            
            total_eval_loss += eval_loss.item()
            total_feat_loss += feat_loss.item()
            
            # Compute correlation coefficient for evaluation
            eval_corr += torch.corrcoef(torch.stack([
                outputs['evaluation'].squeeze(),
                target_eval.squeeze()
            ]))[0, 1].item()
            
            # Compute feature detection accuracy
            feat_preds = (outputs['features'] > 0).float()
            feat_accuracy += (feat_preds == target_features).float().mean().item()
    
    # Compute averages
    metrics = {
        'eval_loss': total_eval_loss / len(val_loader),
        'feat_loss': total_feat_loss / len(val_loader),
        'eval_correlation': eval_corr / len(val_loader),
        'feature_accuracy': feat_accuracy / len(val_loader)
    }
    
    return metrics


# Example usage
if __name__ == "__main__":
    # Create a sample board
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    
    # Create converter
    converter = ChessPositionConverter()
    
    # Convert to graph
    graph_data = converter.board_to_graph(board)
    
    print(f"Nodes: {len(graph_data['node_ids'])}")
    print(f"Edges: {len(graph_data['edge_type'])}")
    
    # Create model
    model = ChessGraphNeuralNetwork()
    
    # Prepare batch
    batch = converter.collate_graphs([graph_data])
    batch['target_eval'] = torch.tensor([[0.5]], dtype=torch.float)
    batch['target_features'] = torch.zeros(1, 32, dtype=torch.float)
    
    # Forward pass (just for testing)
    outputs = model(batch)
    
    print(f"Evaluation: {outputs['evaluation'].item():.4f}")
    print(f"Features shape: {outputs['features'].shape}")