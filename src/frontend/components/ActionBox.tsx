import React, { useState } from 'react';
import { Box, Typography, Button, Select, MenuItem, FormControl, InputLabel, SelectChangeEvent } from '@mui/material';
import { useNavigate } from 'react-router-dom';

interface Variation {
    name: string;
    query: string;
}

interface ActionBoxProps {
    title: string;
    type: 'external' | 'internal' | 'variations' | 'info' | 'placeholder';
    url?: string;
    query?: string;
    variations?: Variation[];
    message?: string;
}

const ActionBox: React.FC<ActionBoxProps> = ({ title, type, url, query, variations, message }) => {
    const navigate = useNavigate();
    const [selectedVariation, setSelectedVariation] = useState<string>('');

    const handleClick = () => {
        if (type === 'external' && url) {
            window.open(url, '_blank');
        } else if (type === 'internal' && query) {
            navigate(`/search?q=${encodeURIComponent(query)}`);
        }
    };

    const handleVariationChange = (event: SelectChangeEvent<string>) => {
        const selected = event.target.value;
        setSelectedVariation(selected);
        const variation = variations?.find(v => v.name === selected);
        if (variation) {
            navigate(`/search?q=${encodeURIComponent(variation.query)}`);
        }
    };

    const renderContent = () => {
        switch (type) {
            case 'variations':
                return (
                    <FormControl fullWidth size="small" sx={{ minWidth: 120 }}>
                        <InputLabel id="model-select-label">Select Model</InputLabel>
                        <Select
                            labelId="model-select-label"
                            id="model-select"
                            value={selectedVariation}
                            label="Select Model"
                            onChange={handleVariationChange}
                            sx={{ 
                                '& .MuiSelect-select': { 
                                    cursor: 'pointer',
                                    '&:hover': {
                                        backgroundColor: 'rgba(0, 0, 0, 0.04)'
                                    }
                                }
                            }}
                        >
                            {variations?.map((variation, index) => (
                                <MenuItem 
                                    key={index} 
                                    value={variation.name}
                                    sx={{ cursor: 'pointer' }}
                                >
                                    {variation.name}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                );
            case 'info':
                return (
                    <Typography variant="body2" color="text.secondary">
                        {message}
                    </Typography>
                );
            case 'placeholder':
                return (
                    <Typography variant="body2" color="text.secondary">
                        {message}
                    </Typography>
                );
            default:
                return (
                    <Button 
                        variant="contained" 
                        color="primary" 
                        onClick={handleClick}
                        fullWidth
                    >
                        {title}
                    </Button>
                );
        }
    };

    return (
        <Box
            sx={{
                p: 2,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                mb: 2,
                backgroundColor: 'background.paper',
                '&:hover': {
                    borderColor: 'primary.main',
                    boxShadow: 1
                }
            }}
        >
            <Typography variant="h6" gutterBottom>
                {title}
            </Typography>
            {renderContent()}
        </Box>
    );
};

export default ActionBox; 