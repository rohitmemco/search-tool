import { useState, useCallback, useEffect, useRef } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  Search, TrendingUp, Globe, DollarSign, Star, ExternalLink, Download, AlertTriangle, 
  Loader2, ShoppingCart, Package, Store, Mail, Phone, MapPin, Clock, Building2, 
  BadgeCheck, User, Users, Moon, Sun, Heart, History, Filter, ArrowUpDown, 
  Grid3X3, List, Share2, Copy, Mic, MicOff, X, Check, Sparkles, Zap, 
  ChevronDown, SlidersHorizontal, FileSpreadsheet, GitCompare, Award, Flame
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, AreaChart, Area } from "recharts";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { motion, AnimatePresence } from "framer-motion";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Currency data for switcher
const CURRENCIES = {
  INR: { symbol: "₹", rate: 1, name: "Indian Rupee" },
  USD: { symbol: "$", rate: 0.012, name: "US Dollar" },
  GBP: { symbol: "£", rate: 0.0095, name: "British Pound" },
  EUR: { symbol: "€", rate: 0.011, name: "Euro" },
  AED: { symbol: "AED", rate: 0.044, name: "UAE Dirham" }
};

// Example queries
const EXAMPLE_QUERIES = [
  "iPhone 15 price in India",
  "Dell Laptop under 50000",
  "Nike shoes",
  "Samsung TV 55 inch",
  "Sony headphones",
  "MacBook Pro in USA"
];

// Chart colors
const CHART_COLORS = ["#2563eb", "#7c3aed", "#10b981", "#f59e0b", "#ef4444", "#06b6d4", "#8b5cf6", "#ec4899"];

// ==================== UTILITY HOOKS ====================

// Dark mode hook
const useDarkMode = () => {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem("darkMode", JSON.stringify(isDark));
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  return [isDark, setIsDark];
};

// Favorites hook
const useFavorites = () => {
  const [favorites, setFavorites] = useState(() => {
    const saved = localStorage.getItem("favorites");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("favorites", JSON.stringify(favorites));
  }, [favorites]);

  const addFavorite = (product) => {
    setFavorites(prev => {
      if (prev.some(p => p.name === product.name && p.source === product.source)) {
        return prev;
      }
      return [...prev, { ...product, addedAt: new Date().toISOString() }];
    });
    toast.success("Added to favorites!");
  };

  const removeFavorite = (product) => {
    setFavorites(prev => prev.filter(p => !(p.name === product.name && p.source === product.source)));
    toast.info("Removed from favorites");
  };

  const isFavorite = (product) => {
    return favorites.some(p => p.name === product.name && p.source === product.source);
  };

  return { favorites, addFavorite, removeFavorite, isFavorite };
};

// Search history hook
const useSearchHistory = () => {
  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem("searchHistory");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("searchHistory", JSON.stringify(history));
  }, [history]);

  const addToHistory = (query) => {
    setHistory(prev => {
      const filtered = prev.filter(h => h.query !== query);
      return [{ query, timestamp: new Date().toISOString() }, ...filtered].slice(0, 10);
    });
  };

  const clearHistory = () => {
    setHistory([]);
    toast.info("Search history cleared");
  };

  return { history, addToHistory, clearHistory };
};

// Compare products hook
const useCompare = () => {
  const [compareList, setCompareList] = useState([]);

  const addToCompare = (product) => {
    if (compareList.length >= 4) {
      toast.error("Maximum 4 products can be compared");
      return;
    }
    if (compareList.some(p => p.name === product.name && p.source === product.source)) {
      toast.info("Product already in comparison");
      return;
    }
    setCompareList(prev => [...prev, product]);
    toast.success("Added to comparison");
  };

  const removeFromCompare = (product) => {
    setCompareList(prev => prev.filter(p => !(p.name === product.name && p.source === product.source)));
  };

  const clearCompare = () => setCompareList([]);

  const isInCompare = (product) => {
    return compareList.some(p => p.name === product.name && p.source === product.source);
  };

  return { compareList, addToCompare, removeFromCompare, clearCompare, isInCompare };
};

// ==================== COMPONENTS ====================

// Star rating component
const StarRating = ({ rating }) => {
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  return (
    <div className="flex items-center gap-1">
      {[...Array(5)].map((_, i) => (
        <Star
          key={i}
          className={`w-4 h-4 ${i < fullStars ? "text-amber-400 fill-amber-400" : i === fullStars && hasHalfStar ? "text-amber-400 fill-amber-400/50" : "text-slate-200 dark:text-slate-600"}`}
        />
      ))}
      <span className="ml-1 text-sm text-slate-600 dark:text-slate-400">{rating.toFixed(1)}</span>
    </div>
  );
};

// Availability badge
const AvailabilityBadge = ({ status }) => {
  const styles = {
    "In Stock": "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800",
    "Limited Stock": "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800",
    "Pre-Order": "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800"
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || styles["In Stock"]}`}>
      {status}
    </span>
  );
};

// Best Deal Badge
const BestDealBadge = ({ product, allProducts }) => {
  const prices = allProducts.map(p => p.price);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  const minPrice = Math.min(...prices);
  
  // Best deal: good rating + price below average
  const isBestDeal = product.rating >= 4.0 && product.price <= avgPrice * 0.85;
  const isLowestPrice = product.price === minPrice;
  
  if (isLowestPrice) {
    return (
      <div className="absolute top-2 left-2 z-10">
        <Badge className="bg-emerald-500 text-white border-0 shadow-lg">
          <Flame className="w-3 h-3 mr-1" /> Lowest Price
        </Badge>
      </div>
    );
  }
  
  if (isBestDeal) {
    return (
      <div className="absolute top-2 left-2 z-10">
        <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white border-0 shadow-lg">
          <Award className="w-3 h-3 mr-1" /> Best Deal
        </Badge>
      </div>
    );
  }
  
  return null;
};

// Currency Switcher
const CurrencySwitcher = ({ selectedCurrency, onCurrencyChange }) => {
  return (
    <Select value={selectedCurrency} onValueChange={onCurrencyChange}>
      <SelectTrigger className="w-28 h-9 text-sm" data-testid="currency-switcher">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {Object.entries(CURRENCIES).map(([code, data]) => (
          <SelectItem key={code} value={code}>
            {data.symbol} {code}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

// Dark Mode Toggle
const DarkModeToggle = ({ isDark, onToggle }) => {
  return (
    <Button
      variant="outline"
      size="icon"
      onClick={onToggle}
      className="rounded-full"
      data-testid="dark-mode-toggle"
    >
      {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
    </Button>
  );
};

// View Toggle (Grid/List)
const ViewToggle = ({ view, onViewChange }) => {
  return (
    <div className="flex items-center border rounded-lg p-1 dark:border-slate-700">
      <Button
        variant={view === "grid" ? "secondary" : "ghost"}
        size="sm"
        onClick={() => onViewChange("grid")}
        className="px-2"
        data-testid="view-grid"
      >
        <Grid3X3 className="w-4 h-4" />
      </Button>
      <Button
        variant={view === "list" ? "secondary" : "ghost"}
        size="sm"
        onClick={() => onViewChange("list")}
        className="px-2"
        data-testid="view-list"
      >
        <List className="w-4 h-4" />
      </Button>
    </div>
  );
};

// Sort Dropdown
const SortDropdown = ({ sortBy, onSortChange }) => {
  const sortOptions = [
    { value: "relevance", label: "Relevance" },
    { value: "price-low", label: "Price: Low to High" },
    { value: "price-high", label: "Price: High to Low" },
    { value: "rating", label: "Highest Rated" },
    { value: "name", label: "Name A-Z" }
  ];

  return (
    <Select value={sortBy} onValueChange={onSortChange}>
      <SelectTrigger className="w-44 h-9 text-sm" data-testid="sort-dropdown">
        <ArrowUpDown className="w-3 h-3 mr-2" />
        <SelectValue placeholder="Sort by" />
      </SelectTrigger>
      <SelectContent>
        {sortOptions.map(option => (
          <SelectItem key={option.value} value={option.value}>
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

// Price Range Slider
const PriceRangeFilter = ({ minPrice, maxPrice, value, onChange }) => {
  const [localValue, setLocalValue] = useState(value);
  
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-600 dark:text-slate-400">Price Range</span>
        <span className="font-medium dark:text-slate-300">
          {localValue[0].toLocaleString()} - {localValue[1].toLocaleString()}
        </span>
      </div>
      <Slider
        min={minPrice}
        max={maxPrice}
        step={Math.ceil((maxPrice - minPrice) / 100)}
        value={localValue}
        onValueChange={setLocalValue}
        onValueCommit={onChange}
        className="w-full"
        data-testid="price-slider"
      />
    </div>
  );
};

// Filter Panel
const FilterPanel = ({ 
  filters, 
  onFiltersChange, 
  availableSources, 
  priceRange,
  onReset,
  advancedFilters
}) => {
  const hasAdvancedFilters = advancedFilters && (
    advancedFilters.models?.length > 0 ||
    advancedFilters.colors?.length > 0 ||
    advancedFilters.sizes?.length > 0 ||
    advancedFilters.brands?.length > 0 ||
    advancedFilters.materials?.length > 0 ||
    Object.keys(advancedFilters.specifications || {}).length > 0
  );

  return (
    <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2 dark:text-white">
          <SlidersHorizontal className="w-4 h-4" /> Filters
        </h3>
        <Button variant="ghost" size="sm" onClick={onReset} data-testid="reset-filters">
          Reset
        </Button>
      </div>
      
      <div className="space-y-6">
        {/* Price Range */}
        <PriceRangeFilter
          minPrice={priceRange[0]}
          maxPrice={priceRange[1]}
          value={filters.priceRange}
          onChange={(value) => onFiltersChange({ ...filters, priceRange: value })}
        />
        
        {/* Rating Filter */}
        <div className="space-y-2">
          <span className="text-sm text-slate-600 dark:text-slate-400">Minimum Rating</span>
          <div className="flex gap-2">
            {[0, 3, 3.5, 4, 4.5].map(rating => (
              <Button
                key={rating}
                variant={filters.minRating === rating ? "secondary" : "outline"}
                size="sm"
                onClick={() => onFiltersChange({ ...filters, minRating: rating })}
                className="text-xs"
              >
                {rating === 0 ? "All" : `${rating}+`}
              </Button>
            ))}
          </div>
        </div>
        
        {/* Availability Filter */}
        <div className="space-y-2">
          <span className="text-sm text-slate-600 dark:text-slate-400">Availability</span>
          <div className="space-y-2">
            {["In Stock", "Limited Stock", "Pre-Order"].map(status => (
              <label key={status} className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  checked={filters.availability.includes(status)}
                  onCheckedChange={(checked) => {
                    const newAvailability = checked
                      ? [...filters.availability, status]
                      : filters.availability.filter(s => s !== status);
                    onFiltersChange({ ...filters, availability: newAvailability });
                  }}
                />
                <span className="text-sm dark:text-slate-300">{status}</span>
              </label>
            ))}
          </div>
        </div>
        
        {/* Source Type Filter */}
        <div className="space-y-2">
          <span className="text-sm text-slate-600 dark:text-slate-400">Source Type</span>
          <div className="space-y-2">
            {["Global Suppliers", "Local Markets", "Online Marketplaces"].map(type => (
              <label key={type} className="flex items-center gap-2 cursor-pointer">
                <Checkbox
                  checked={filters.sourceTypes.includes(type)}
                  onCheckedChange={(checked) => {
                    const newTypes = checked
                      ? [...filters.sourceTypes, type]
                      : filters.sourceTypes.filter(t => t !== type);
                    onFiltersChange({ ...filters, sourceTypes: newTypes });
                  }}
                />
                <span className="text-sm dark:text-slate-300">{type}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Advanced Filters Section */}
        {hasAdvancedFilters && (
          <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
            <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-500" />
              Product Specific Filters
            </h4>
            
            {/* Brand Filter */}
            {advancedFilters.brands?.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-sm text-slate-600 dark:text-slate-400">Brand</span>
                <Select 
                  value={filters.selectedBrand || "all"} 
                  onValueChange={(value) => onFiltersChange({ ...filters, selectedBrand: value === "all" ? null : value })}
                >
                  <SelectTrigger className="w-full" data-testid="brand-filter">
                    <SelectValue placeholder="All Brands" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Brands</SelectItem>
                    {advancedFilters.brands.map(brand => (
                      <SelectItem key={brand} value={brand}>{brand}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            
            {/* Model Filter */}
            {advancedFilters.models?.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-sm text-slate-600 dark:text-slate-400">Model</span>
                <Select 
                  value={filters.selectedModel || "all"} 
                  onValueChange={(value) => onFiltersChange({ ...filters, selectedModel: value === "all" ? null : value })}
                >
                  <SelectTrigger className="w-full" data-testid="model-filter">
                    <SelectValue placeholder="All Models" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Models</SelectItem>
                    {advancedFilters.models.map(model => (
                      <SelectItem key={model} value={model}>{model}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            
            {/* Color Filter */}
            {advancedFilters.colors?.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-sm text-slate-600 dark:text-slate-400">Color</span>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={!filters.selectedColor ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => onFiltersChange({ ...filters, selectedColor: null })}
                    className="text-xs"
                    data-testid="color-filter-all"
                  >
                    All
                  </Button>
                  {advancedFilters.colors.map(color => (
                    <Button
                      key={color}
                      variant={filters.selectedColor === color ? "secondary" : "outline"}
                      size="sm"
                      onClick={() => onFiltersChange({ ...filters, selectedColor: color })}
                      className="text-xs gap-1"
                      data-testid={`color-filter-${color.toLowerCase()}`}
                    >
                      <span 
                        className="w-3 h-3 rounded-full border border-slate-300" 
                        style={{ backgroundColor: color.toLowerCase() === 'white' ? '#f8fafc' : color.toLowerCase() }}
                      />
                      {color}
                    </Button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Size Filter */}
            {advancedFilters.sizes?.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-sm text-slate-600 dark:text-slate-400">Size</span>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={!filters.selectedSize ? "secondary" : "outline"}
                    size="sm"
                    onClick={() => onFiltersChange({ ...filters, selectedSize: null })}
                    className="text-xs"
                    data-testid="size-filter-all"
                  >
                    All
                  </Button>
                  {advancedFilters.sizes.map(size => (
                    <Button
                      key={size}
                      variant={filters.selectedSize === size ? "secondary" : "outline"}
                      size="sm"
                      onClick={() => onFiltersChange({ ...filters, selectedSize: size })}
                      className="text-xs"
                      data-testid={`size-filter-${size}`}
                    >
                      {size}
                    </Button>
                  ))}
                </div>
              </div>
            )}
            
            {/* Material Filter */}
            {advancedFilters.materials?.length > 0 && (
              <div className="space-y-2 mb-4">
                <span className="text-sm text-slate-600 dark:text-slate-400">Material</span>
                <Select 
                  value={filters.selectedMaterial || "all"} 
                  onValueChange={(value) => onFiltersChange({ ...filters, selectedMaterial: value === "all" ? null : value })}
                >
                  <SelectTrigger className="w-full" data-testid="material-filter">
                    <SelectValue placeholder="All Materials" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Materials</SelectItem>
                    {advancedFilters.materials.map(material => (
                      <SelectItem key={material} value={material}>{material}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            
            {/* Dynamic Specifications Filters */}
            {advancedFilters.specifications && Object.keys(advancedFilters.specifications).length > 0 && (
              <div className="space-y-4">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Specifications</span>
                {Object.entries(advancedFilters.specifications).map(([specName, specOptions]) => (
                  specOptions && specOptions.length > 0 && (
                    <div key={specName} className="space-y-2">
                      <span className="text-xs text-slate-500 dark:text-slate-400">{specName}</span>
                      <Select 
                        value={filters.selectedSpecs?.[specName] || "all"} 
                        onValueChange={(value) => {
                          const newSpecs = { ...(filters.selectedSpecs || {}) };
                          if (value === "all") {
                            delete newSpecs[specName];
                          } else {
                            newSpecs[specName] = value;
                          }
                          onFiltersChange({ ...filters, selectedSpecs: newSpecs });
                        }}
                      >
                        <SelectTrigger className="w-full" data-testid={`spec-filter-${specName.toLowerCase().replace(/\s+/g, '-')}`}>
                          <SelectValue placeholder={`All ${specName}`} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All {specName}</SelectItem>
                          {specOptions.map(option => (
                            <SelectItem key={option} value={option}>{option}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

// Voice Search Button
const VoiceSearchButton = ({ onResult, isListening, setIsListening }) => {
  const recognitionRef = useRef(null);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error("Voice search not supported in this browser");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
      setIsListening(false);
    };

    recognitionRef.current.onerror = () => {
      setIsListening(false);
      toast.error("Voice recognition error");
    };

    recognitionRef.current.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current.start();
    setIsListening(true);
    toast.info("Listening... Speak now");
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={isListening ? stopListening : startListening}
      className={`rounded-full ${isListening ? "bg-red-100 border-red-300 text-red-600" : ""}`}
      data-testid="voice-search"
    >
      {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
    </Button>
  );
};

// Search History Panel
const SearchHistoryPanel = ({ history, onSearch, onClear }) => {
  if (history.length === 0) return null;

  return (
    <Card className="p-4 dark:bg-slate-800 dark:border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold flex items-center gap-2 text-sm dark:text-white">
          <History className="w-4 h-4" /> Recent Searches
        </h3>
        <Button variant="ghost" size="sm" onClick={onClear} className="text-xs">
          Clear All
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {history.slice(0, 6).map((item, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSearch(item.query)}
            className="text-xs dark:border-slate-600 dark:text-slate-300"
            data-testid={`history-item-${index}`}
          >
            {item.query}
          </Button>
        ))}
      </div>
    </Card>
  );
};

// Favorites Panel
const FavoritesPanel = ({ favorites, onRemove, onSearch, selectedCurrency }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const convertPrice = (price, originalCurrency) => {
    const inINR = originalCurrency === "INR" ? price : price / CURRENCIES[originalCurrency].rate;
    return inINR * CURRENCIES[selectedCurrency].rate;
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" className="relative" data-testid="favorites-button">
          <Heart className={`w-4 h-4 ${favorites.length > 0 ? "fill-red-500 text-red-500" : ""}`} />
          {favorites.length > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {favorites.length}
            </span>
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-500 fill-red-500" />
            My Favorites ({favorites.length})
          </DialogTitle>
        </DialogHeader>
        {favorites.length === 0 ? (
          <div className="text-center py-8 text-slate-500">
            <Heart className="w-12 h-12 mx-auto mb-3 text-slate-300" />
            <p>No favorites yet</p>
            <p className="text-sm">Click the heart icon on products to save them</p>
          </div>
        ) : (
          <div className="space-y-3">
            {favorites.map((product, index) => (
              <div key={index} className="flex items-center gap-4 p-3 border rounded-lg dark:border-slate-700">
                <img src={product.image} alt={product.name} className="w-16 h-16 object-cover rounded" />
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium truncate dark:text-white">{product.name}</h4>
                  <p className="text-sm text-slate-500">{product.source}</p>
                  <p className="font-semibold text-blue-600">
                    {CURRENCIES[selectedCurrency].symbol}
                    {convertPrice(product.price, product.currency_code || "INR").toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => onSearch(product.name)}>
                    Search
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => onRemove(product)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

// Product Comparison Modal
const CompareModal = ({ compareList, onRemove, onClear, selectedCurrency }) => {
  const [isOpen, setIsOpen] = useState(false);

  const convertPrice = (price, originalCurrency) => {
    const inINR = originalCurrency === "INR" ? price : price / CURRENCIES[originalCurrency].rate;
    return inINR * CURRENCIES[selectedCurrency].rate;
  };

  if (compareList.length === 0) return null;

  return (
    <>
      {/* Floating Compare Button */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed bottom-6 right-6 z-50"
      >
        <Button
          onClick={() => setIsOpen(true)}
          className="btn-gradient text-white rounded-full px-6 py-6 shadow-xl"
          data-testid="compare-button"
        >
          <GitCompare className="w-5 h-5 mr-2" />
          Compare ({compareList.length})
        </Button>
      </motion.div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2">
                <GitCompare className="w-5 h-5 text-blue-600" />
                Compare Products ({compareList.length}/4)
              </DialogTitle>
              <Button variant="ghost" size="sm" onClick={onClear}>
                Clear All
              </Button>
            </div>
          </DialogHeader>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            {compareList.map((product, index) => (
              <Card key={index} className="relative dark:bg-slate-800">
                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-2 right-2 z-10"
                  onClick={() => onRemove(product)}
                >
                  <X className="w-4 h-4" />
                </Button>
                <CardContent className="p-4">
                  <img src={product.image} alt={product.name} className="w-full h-32 object-cover rounded mb-3" />
                  <h4 className="font-medium text-sm mb-2 line-clamp-2 dark:text-white">{product.name}</h4>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Price</span>
                      <span className="font-bold text-blue-600">
                        {CURRENCIES[selectedCurrency].symbol}
                        {convertPrice(product.price, product.currency_code || "INR").toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Rating</span>
                      <span className="flex items-center">
                        <Star className="w-3 h-3 text-amber-400 fill-amber-400 mr-1" />
                        {product.rating}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Source</span>
                      <span className="dark:text-slate-300">{product.source}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Status</span>
                      <AvailabilityBadge status={product.availability} />
                    </div>
                  </div>
                  
                  <a
                    href={product.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block mt-3"
                  >
                    <Button variant="outline" size="sm" className="w-full">
                      View <ExternalLink className="w-3 h-3 ml-1" />
                    </Button>
                  </a>
                </CardContent>
              </Card>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

// Share Results Component
const ShareResults = ({ query, resultsCount }) => {
  const shareUrl = `${window.location.origin}?q=${encodeURIComponent(query)}`;
  
  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareUrl);
    toast.success("Link copied to clipboard!");
  };

  const shareToTwitter = () => {
    const text = `Found ${resultsCount} results for "${query}" on PriceNexus - AI-Powered Price Comparison`;
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl)}`, "_blank");
  };

  const shareToWhatsApp = () => {
    const text = `Check out prices for "${query}" - ${resultsCount} results found!`;
    window.open(`https://wa.me/?text=${encodeURIComponent(text + " " + shareUrl)}`, "_blank");
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" data-testid="share-button">
          <Share2 className="w-4 h-4 mr-2" /> Share
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem onClick={copyToClipboard}>
          <Copy className="w-4 h-4 mr-2" /> Copy Link
        </DropdownMenuItem>
        <DropdownMenuItem onClick={shareToTwitter}>
          <span className="mr-2">𝕏</span> Share on X
        </DropdownMenuItem>
        <DropdownMenuItem onClick={shareToWhatsApp}>
          <span className="mr-2">💬</span> Share on WhatsApp
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

// Export to Excel
const ExportToExcel = ({ results, query }) => {
  const exportCSV = () => {
    const headers = ["Name", "Price", "Currency", "Source", "Rating", "Availability", "Description", "Vendor", "Address", "Phone", "Email"];
    const rows = results.map(r => [
      r.name,
      r.price,
      r.currency_code,
      r.source,
      r.rating,
      r.availability,
      r.description,
      r.vendor?.vendor_name || "",
      r.vendor?.vendor_address || "",
      r.vendor?.vendor_phone || "",
      r.vendor?.vendor_email || ""
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.map(cell => `"${cell}"`).join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${query.replace(/\s+/g, "_")}_results.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Excel/CSV exported!");
  };

  return (
    <Button variant="outline" size="sm" onClick={exportCSV} data-testid="export-excel">
      <FileSpreadsheet className="w-4 h-4 mr-2" /> Export Excel
    </Button>
  );
};

// Price Distribution Chart
const PriceDistributionChart = ({ results }) => {
  // Create price buckets
  const prices = results.map(r => r.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const bucketSize = (maxPrice - minPrice) / 6;
  
  const buckets = [];
  for (let i = 0; i < 6; i++) {
    const low = minPrice + (bucketSize * i);
    const high = minPrice + (bucketSize * (i + 1));
    const count = prices.filter(p => p >= low && (i === 5 ? p <= high : p < high)).length;
    buckets.push({
      range: `${Math.round(low / 1000)}k-${Math.round(high / 1000)}k`,
      count,
      percentage: Math.round((count / results.length) * 100)
    });
  }

  return (
    <div className="chart-container dark:bg-slate-800 dark:border-slate-700" data-testid="price-distribution-chart">
      <h3 className="chart-title dark:text-white">Price Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={buckets}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="range" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip formatter={(value) => [`${value} products`, "Count"]} />
          <Area 
            type="monotone" 
            dataKey="count" 
            stroke="#7c3aed" 
            fill="url(#colorGradientArea)" 
            strokeWidth={2}
          />
          <defs>
            <linearGradient id="colorGradientArea" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7c3aed" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.05} />
            </linearGradient>
          </defs>
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

// Similar Products Section
const SimilarProducts = ({ currentProduct, onSearch }) => {
  const [similar, setSimilar] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSimilar = async () => {
      if (!currentProduct) return;
      setLoading(true);
      try {
        const response = await axios.post(`${API}/similar-products`, {
          product_name: currentProduct,
          category: "General"
        });
        setSimilar(response.data);
      } catch (error) {
        console.error("Error fetching similar products:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSimilar();
  }, [currentProduct]);

  if (!similar || loading) return null;

  return (
    <Card className="p-4 dark:bg-slate-800 dark:border-slate-700" data-testid="similar-products">
      <h3 className="font-semibold flex items-center gap-2 mb-3 dark:text-white">
        <Sparkles className="w-4 h-4 text-violet-500" /> Similar Products
      </h3>
      <div className="flex flex-wrap gap-2">
        {similar.similar?.slice(0, 5).map((product, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSearch(product)}
            className="text-xs dark:border-slate-600 dark:text-slate-300"
          >
            {product}
          </Button>
        ))}
      </div>
      {similar.complementary?.length > 0 && (
        <div className="mt-3 pt-3 border-t dark:border-slate-700">
          <p className="text-xs text-slate-500 mb-2">Often bought together:</p>
          <div className="flex flex-wrap gap-2">
            {similar.complementary.slice(0, 3).map((product, index) => (
              <Button
                key={index}
                variant="ghost"
                size="sm"
                onClick={() => onSearch(product)}
                className="text-xs"
              >
                + {product}
              </Button>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
};

// Smart Recommendations
const SmartRecommendations = ({ searchHistory, onSearch }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (searchHistory.length === 0) return;
      setLoading(true);
      try {
        const response = await axios.post(`${API}/smart-recommendations`, {
          recent_searches: searchHistory.map(h => h.query),
          current_product: searchHistory[0]?.query || ""
        });
        setRecommendations(response.data);
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecommendations();
  }, [searchHistory]);

  if (!recommendations || loading) return null;

  return (
    <Card className="p-4 dark:bg-slate-800 dark:border-slate-700" data-testid="smart-recommendations">
      <h3 className="font-semibold flex items-center gap-2 mb-3 dark:text-white">
        <Zap className="w-4 h-4 text-amber-500" /> Recommended for You
      </h3>
      <div className="space-y-2">
        {recommendations.recommendations?.slice(0, 4).map((rec, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer"
            onClick={() => onSearch(rec.name)}
          >
            <div>
              <p className="font-medium text-sm dark:text-white">{rec.name}</p>
              <p className="text-xs text-slate-500">{rec.reason}</p>
            </div>
            <Badge variant="outline" className="text-xs">{rec.category}</Badge>
          </div>
        ))}
      </div>
      {recommendations.trending?.length > 0 && (
        <div className="mt-3 pt-3 border-t dark:border-slate-700">
          <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
            <Flame className="w-3 h-3 text-orange-500" /> Trending Now
          </p>
          <div className="flex flex-wrap gap-2">
            {recommendations.trending.slice(0, 4).map((item, index) => (
              <Button
                key={index}
                variant="outline"
                size="sm"
                onClick={() => onSearch(item)}
                className="text-xs"
              >
                {item}
              </Button>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
};

// Vendor Info Modal Component
const VendorInfoModal = ({ vendor, productName }) => {
  if (!vendor) return null;
  
  const getVerificationColor = (status) => {
    switch (status) {
      case "Verified Seller": return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400";
      case "Premium Vendor": return "bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-900/30 dark:text-violet-400";
      case "Trusted Supplier": return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400";
      case "Gold Member": return "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400";
      default: return "bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-700 dark:text-slate-300";
    }
  };
  
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="mt-3 w-full text-xs" data-testid="view-vendor-btn">
          <Building2 className="w-3 h-3 mr-1" />
          View Vendor Details
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg dark:bg-slate-800" data-testid="vendor-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 font-['Manrope'] dark:text-white">
            <Store className="w-5 h-5 text-blue-600" />
            Vendor Information
          </DialogTitle>
        </DialogHeader>
        <div className="space-y-4 mt-4">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-lg text-slate-800 dark:text-white">{vendor.vendor_name}</h3>
              <p className="text-sm text-slate-500">{vendor.vendor_type}</p>
            </div>
            <Badge variant="outline" className={getVerificationColor(vendor.verification_status)}>
              <BadgeCheck className="w-3 h-3 mr-1" />
              {vendor.verification_status}
            </Badge>
          </div>
          
          <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1">Selling</p>
            <p className="text-sm font-medium text-slate-800 dark:text-white">{productName}</p>
          </div>
          
          <div className="grid grid-cols-1 gap-3">
            <div className="flex items-center gap-3 p-3 bg-blue-50/50 dark:bg-blue-900/20 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center">
                <Mail className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Email</p>
                <a href={`mailto:${vendor.vendor_email}`} className="text-sm font-medium text-blue-600 hover:underline">
                  {vendor.vendor_email}
                </a>
              </div>
            </div>
            
            <div className="flex items-center gap-3 p-3 bg-emerald-50/50 dark:bg-emerald-900/20 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-emerald-100 dark:bg-emerald-800 flex items-center justify-center">
                <Phone className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Phone</p>
                <a href={`tel:${vendor.vendor_phone}`} className="text-sm font-medium text-emerald-600 hover:underline">
                  {vendor.vendor_phone}
                </a>
              </div>
            </div>
            
            <div className="flex items-start gap-3 p-3 bg-violet-50/50 dark:bg-violet-900/20 rounded-lg">
              <div className="w-10 h-10 rounded-full bg-violet-100 dark:bg-violet-800 flex items-center justify-center flex-shrink-0">
                <MapPin className="w-5 h-5 text-violet-600 dark:text-violet-400" />
              </div>
              <div>
                <p className="text-xs text-slate-500 dark:text-slate-400">Address</p>
                <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{vendor.vendor_address}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{vendor.vendor_city}, {vendor.vendor_country}</p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="text-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <Clock className="w-4 h-4 mx-auto text-slate-400 mb-1" />
              <p className="text-xs text-slate-500 dark:text-slate-400">Response Time</p>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{vendor.response_time}</p>
            </div>
            <div className="text-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <Building2 className="w-4 h-4 mx-auto text-slate-400 mb-1" />
              <p className="text-xs text-slate-500 dark:text-slate-400">In Business</p>
              <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{vendor.years_in_business} years</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400 pt-2 border-t dark:border-slate-700">
            <Clock className="w-4 h-4" />
            <span>{vendor.business_hours}</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Product Card Component
const ProductCard = ({ product, index, allProducts, view, selectedCurrency, onFavoriteToggle, isFavorite, onCompareToggle, isInCompare }) => {
  const convertPrice = (price) => {
    const originalCode = product.currency_code || "INR";
    const inINR = originalCode === "INR" ? price : price / CURRENCIES[originalCode].rate;
    return inINR * CURRENCIES[selectedCurrency].rate;
  };

  const convertedPrice = convertPrice(product.price);

  if (view === "list") {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.03, duration: 0.3 }}
        className="flex items-center gap-4 p-4 bg-white dark:bg-slate-800 border dark:border-slate-700 rounded-xl hover:shadow-lg transition-all"
        data-testid={`product-card-${index}`}
      >
        <div className="relative">
          <img src={product.image} alt={product.name} className="w-20 h-20 object-cover rounded-lg" />
          <BestDealBadge product={product} allProducts={allProducts} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-800 dark:text-white truncate">{product.name}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">{product.source}</p>
          <div className="flex items-center gap-3 mt-1">
            <StarRating rating={product.rating} />
            <AvailabilityBadge status={product.availability} />
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-blue-600">
            {CURRENCIES[selectedCurrency].symbol}{convertedPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <div className="flex gap-2 mt-2">
            <Button variant="ghost" size="icon" onClick={() => onFavoriteToggle(product)}>
              <Heart className={`w-4 h-4 ${isFavorite ? "fill-red-500 text-red-500" : ""}`} />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => onCompareToggle(product)}>
              <GitCompare className={`w-4 h-4 ${isInCompare ? "text-blue-600" : ""}`} />
            </Button>
            <a href={product.source_url} target="_blank" rel="noopener noreferrer">
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4" />
              </Button>
            </a>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className="product-card relative dark:bg-slate-800 dark:border-slate-700"
      data-testid={`product-card-${index}`}
    >
      <BestDealBadge product={product} allProducts={allProducts} />
      
      {/* Favorite & Compare buttons */}
      <div className="absolute top-2 right-2 z-10 flex gap-1">
        <Button
          variant="secondary"
          size="icon"
          className="w-8 h-8 rounded-full bg-white/80 dark:bg-slate-800/80 backdrop-blur"
          onClick={() => onFavoriteToggle(product)}
        >
          <Heart className={`w-4 h-4 ${isFavorite ? "fill-red-500 text-red-500" : ""}`} />
        </Button>
        <Button
          variant="secondary"
          size="icon"
          className="w-8 h-8 rounded-full bg-white/80 dark:bg-slate-800/80 backdrop-blur"
          onClick={() => onCompareToggle(product)}
        >
          <GitCompare className={`w-4 h-4 ${isInCompare ? "text-blue-600" : ""}`} />
        </Button>
      </div>

      <img src={product.image} alt={product.name} className="product-card-image" loading="lazy" />
      <div className="product-card-content">
        <h3 className="product-card-title dark:text-white">{product.name}</h3>
        <p className="product-card-price">
          {CURRENCIES[selectedCurrency].symbol}{convertedPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
        <div className="product-card-source dark:bg-slate-700 dark:text-slate-300">
          <Store className="w-3 h-3" />
          {product.source}
        </div>
        <div className="flex items-center justify-between mt-2">
          <StarRating rating={product.rating} />
          <AvailabilityBadge status={product.availability} />
        </div>
        <p className="product-card-description dark:text-slate-400">{product.description}</p>
        
        {product.vendor && (
          <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Vendor</p>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 truncate">{product.vendor.vendor_name}</p>
            <VendorInfoModal vendor={product.vendor} productName={product.name} />
          </div>
        )}
        
        <a
          href={product.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-3 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
          data-testid={`view-source-${index}`}
        >
          View on {product.source}
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </motion.div>
  );
};

// Price Summary Component
const PriceSummary = ({ results, selectedCurrency }) => {
  if (!results.length) return null;
  
  const convertPrice = (price, originalCode) => {
    const inINR = originalCode === "INR" ? price : price / CURRENCIES[originalCode].rate;
    return inINR * CURRENCIES[selectedCurrency].rate;
  };
  
  const prices = results.map(r => convertPrice(r.price, r.currency_code || "INR"));
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
  const symbol = CURRENCIES[selectedCurrency].symbol;
  
  return (
    <div className="price-summary-grid" data-testid="price-summary">
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="price-summary-card min dark:bg-emerald-900/20 dark:border-emerald-800">
        <p className="price-summary-label text-emerald-700 dark:text-emerald-400">Lowest Price</p>
        <p className="price-summary-value text-emerald-600 dark:text-emerald-400">
          {symbol}{minPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="price-summary-card max dark:bg-red-900/20 dark:border-red-800">
        <p className="price-summary-label text-red-700 dark:text-red-400">Highest Price</p>
        <p className="price-summary-value text-red-600 dark:text-red-400">
          {symbol}{maxPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }} className="price-summary-card avg dark:bg-blue-900/20 dark:border-blue-800">
        <p className="price-summary-label text-blue-700 dark:text-blue-400">Average Price</p>
        <p className="price-summary-value text-blue-600 dark:text-blue-400">
          {symbol}{avgPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </motion.div>
    </div>
  );
};

// Price Comparison Chart
const PriceComparisonChart = ({ results, selectedCurrency }) => {
  const convertPrice = (price, originalCode) => {
    const inINR = originalCode === "INR" ? price : price / CURRENCIES[originalCode].rate;
    return inINR * CURRENCIES[selectedCurrency].rate;
  };

  const sourceData = {};
  results.forEach(r => {
    if (!sourceData[r.source]) {
      sourceData[r.source] = { total: 0, count: 0 };
    }
    sourceData[r.source].total += convertPrice(r.price, r.currency_code || "INR");
    sourceData[r.source].count += 1;
  });
  
  const chartData = Object.entries(sourceData)
    .map(([source, data]) => ({
      source: source.length > 12 ? source.substring(0, 12) + "..." : source,
      fullSource: source,
      avgPrice: Math.round(data.total / data.count)
    }))
    .sort((a, b) => a.avgPrice - b.avgPrice)
    .slice(0, 8);
  
  return (
    <div className="chart-container dark:bg-slate-800 dark:border-slate-700" data-testid="price-chart">
      <h3 className="chart-title dark:text-white">Price Comparison by Source</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="source" tick={{ fontSize: 12, fill: "#64748b" }} angle={-45} textAnchor="end" height={60} />
          <YAxis tick={{ fontSize: 12, fill: "#64748b" }} tickFormatter={(value) => `${value.toLocaleString()}`} />
          <Tooltip formatter={(value) => [value.toLocaleString(), "Avg Price"]} labelFormatter={(label, payload) => payload[0]?.payload?.fullSource || label} contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }} />
          <Bar dataKey="avgPrice" fill="url(#colorGradient)" radius={[4, 4, 0, 0]} />
          <defs>
            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563eb" />
              <stop offset="100%" stopColor="#7c3aed" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

// Source Distribution Chart
const SourceDistributionChart = ({ results }) => {
  const sourceCount = {};
  results.forEach(r => {
    sourceCount[r.source] = (sourceCount[r.source] || 0) + 1;
  });
  
  const chartData = Object.entries(sourceCount)
    .map(([source, count]) => ({ name: source, value: count }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
  
  return (
    <div className="chart-container dark:bg-slate-800 dark:border-slate-700" data-testid="source-distribution-chart">
      <h3 className="chart-title dark:text-white">Results by Source</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value" label={({ name, percent }) => `${name.substring(0, 10)}${name.length > 10 ? "..." : ""} (${(percent * 100).toFixed(0)}%)`} labelLine={false}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => [value, "Products"]} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

// Data Sources Section
const DataSourcesSection = ({ dataSources }) => {
  const getSourceIcon = (type) => {
    switch (type) {
      case "Global Supplier": return <Globe className="w-5 h-5 text-blue-600" />;
      case "Local Market": return <Store className="w-5 h-5 text-emerald-600" />;
      default: return <ShoppingCart className="w-5 h-5 text-violet-600" />;
    }
  };
  
  const getSourceBadgeColor = (type) => {
    switch (type) {
      case "Global Supplier": return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400";
      case "Local Market": return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400";
      default: return "bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-900/30 dark:text-violet-400";
    }
  };
  
  return (
    <div data-testid="data-sources">
      <h3 className="text-lg font-semibold text-slate-800 dark:text-white mb-4 font-['Manrope']">Data Sources</h3>
      <div className="data-sources-grid">
        {dataSources.map((source, index) => (
          <a key={index} href={source.url} target="_blank" rel="noopener noreferrer" className="data-source-card dark:bg-slate-800 dark:border-slate-700" data-testid={`data-source-${index}`}>
            {getSourceIcon(source.type)}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-slate-800 dark:text-white truncate">{source.name}</p>
              <Badge variant="outline" className={`mt-1 ${getSourceBadgeColor(source.type)}`}>{source.type}</Badge>
            </div>
            <ExternalLink className="w-4 h-4 text-slate-400" />
          </a>
        ))}
      </div>
    </div>
  );
};

// Vendors Section
const VendorsSection = ({ results }) => {
  const vendorsMap = new Map();
  results.forEach(product => {
    if (product.vendor) {
      const key = product.vendor.vendor_email;
      if (!vendorsMap.has(key)) {
        vendorsMap.set(key, { ...product.vendor, products: [product.name], lowestPrice: product.price, currencySymbol: product.currency_symbol });
      } else {
        const existing = vendorsMap.get(key);
        existing.products.push(product.name);
        if (product.price < existing.lowestPrice) existing.lowestPrice = product.price;
      }
    }
  });
  
  const vendors = Array.from(vendorsMap.values());
  
  const getVendorTypeColor = (type) => {
    if (type.includes("Global")) return "bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400";
    if (type.includes("Local")) return "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-400";
    return "bg-violet-50 text-violet-700 border-violet-200 dark:bg-violet-900/30 dark:text-violet-400";
  };
  
  const getVerificationColor = (status) => {
    switch (status) {
      case "Verified Seller": return "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400";
      case "Premium Vendor": return "bg-violet-100 text-violet-700 dark:bg-violet-900/50 dark:text-violet-400";
      case "Trusted Supplier": return "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400";
      case "Gold Member": return "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400";
      default: return "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300";
    }
  };
  
  return (
    <div data-testid="vendors-section">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white font-['Manrope']">
          <Users className="w-5 h-5 inline mr-2 text-blue-600" />
          Vendor Directory ({vendors.length} vendors)
        </h3>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {vendors.map((vendor, index) => (
          <motion.div key={index} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.05 }} className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-5 hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-800 transition-all" data-testid={`vendor-card-${index}`}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h4 className="font-semibold text-slate-800 dark:text-white text-lg">{vendor.vendor_name}</h4>
                <div className="flex items-center gap-2 mt-1">
                  <Badge variant="outline" className={getVendorTypeColor(vendor.vendor_type)}>{vendor.vendor_type}</Badge>
                  <Badge className={getVerificationColor(vendor.verification_status)}>
                    <BadgeCheck className="w-3 h-3 mr-1" />{vendor.verification_status}
                  </Badge>
                </div>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 dark:text-slate-400">From</p>
                <p className="text-lg font-bold text-blue-600">{vendor.currencySymbol}{vendor.lowestPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <Mail className="w-4 h-4 text-blue-500" />
                <a href={`mailto:${vendor.vendor_email}`} className="hover:text-blue-600 hover:underline truncate">{vendor.vendor_email}</a>
              </div>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <Phone className="w-4 h-4 text-emerald-500" />
                <a href={`tel:${vendor.vendor_phone}`} className="hover:text-emerald-600 hover:underline">{vendor.vendor_phone}</a>
              </div>
              <div className="flex items-start gap-2 text-slate-600 dark:text-slate-300">
                <MapPin className="w-4 h-4 text-violet-500 flex-shrink-0 mt-0.5" />
                <span className="line-clamp-2">{vendor.vendor_address}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300">
                <Globe className="w-4 h-4 text-slate-400" />
                <span>{vendor.vendor_city}, {vendor.vendor_country}</span>
              </div>
            </div>
            <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-100 dark:border-slate-700 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-1"><Clock className="w-3 h-3" />{vendor.response_time}</div>
              <div className="flex items-center gap-1"><Building2 className="w-3 h-3" />{vendor.years_in_business} years in business</div>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
              <p className="text-xs text-slate-500 dark:text-slate-400"><Package className="w-3 h-3 inline mr-1" />{vendor.products.length} product{vendor.products.length > 1 ? 's' : ''} available</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

// Search Unavailable Component
const SearchUnavailable = ({ query }) => {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="search-unavailable dark:bg-amber-900/20 dark:border-amber-700" data-testid="search-unavailable">
      <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
      <h2 className="dark:text-amber-300">Search Unavailable</h2>
      <p className="mb-4 dark:text-amber-200">We couldn't find results for "<strong>{query}</strong>"</p>
      <div className="text-left mt-6">
        <p className="font-medium text-amber-800 dark:text-amber-300 mb-2">Suggestions:</p>
        <ul className="list-disc list-inside text-amber-700 dark:text-amber-400 space-y-1">
          <li>Try using different keywords</li>
          <li>Check the spelling of your search</li>
          <li>Search for a similar or related product</li>
          <li>Use more general terms</li>
        </ul>
      </div>
    </motion.div>
  );
};

// Markdown renderer
const MarkdownContent = ({ content }) => {
  const parseMarkdown = (text) => {
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n/g, '<br />');
  };
  
  return <div className="markdown-content dark:text-slate-300" dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }} />;
};

// ==================== MAIN SEARCH PAGE ====================
const SearchPage = () => {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  const [isListening, setIsListening] = useState(false);
  
  // Feature hooks
  const [isDark, setIsDark] = useDarkMode();
  const { favorites, addFavorite, removeFavorite, isFavorite } = useFavorites();
  const { history, addToHistory, clearHistory } = useSearchHistory();
  const { compareList, addToCompare, removeFromCompare, clearCompare, isInCompare } = useCompare();
  
  // UI state
  const [selectedCurrency, setSelectedCurrency] = useState("INR");
  const [view, setView] = useState("grid");
  const [sortBy, setSortBy] = useState("relevance");
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    priceRange: [0, 1000000],
    minRating: 0,
    availability: ["In Stock", "Limited Stock", "Pre-Order"],
    sourceTypes: ["Global Suppliers", "Local Markets", "Online Marketplaces"],
    // Advanced filters
    selectedBrand: null,
    selectedModel: null,
    selectedColor: null,
    selectedSize: null,
    selectedMaterial: null,
    selectedSpecs: {}
  });
  
  // Store available advanced filters from search results
  const [advancedFilters, setAdvancedFilters] = useState(null);

  // Calculate price range from results
  const priceRange = searchResults?.results?.length > 0
    ? [Math.min(...searchResults.results.map(r => r.price)), Math.max(...searchResults.results.map(r => r.price))]
    : [0, 100000];

  // Filter and sort results
  const filteredResults = searchResults?.results?.filter(r => {
    const price = r.price;
    const meetsPrice = price >= filters.priceRange[0] && price <= filters.priceRange[1];
    const meetsRating = r.rating >= filters.minRating;
    const meetsAvailability = filters.availability.includes(r.availability);
    
    // Advanced filters
    const meetsBrand = !filters.selectedBrand || r.brand === filters.selectedBrand;
    const meetsModel = !filters.selectedModel || r.model === filters.selectedModel;
    const meetsColor = !filters.selectedColor || r.color === filters.selectedColor;
    const meetsSize = !filters.selectedSize || r.size === filters.selectedSize;
    const meetsMaterial = !filters.selectedMaterial || r.material === filters.selectedMaterial;
    
    // Check specifications
    let meetsSpecs = true;
    if (filters.selectedSpecs && Object.keys(filters.selectedSpecs).length > 0) {
      for (const [specName, specValue] of Object.entries(filters.selectedSpecs)) {
        if (r.specifications && r.specifications[specName] !== specValue) {
          meetsSpecs = false;
          break;
        }
      }
    }
    
    return meetsPrice && meetsRating && meetsAvailability && meetsBrand && meetsModel && meetsColor && meetsSize && meetsMaterial && meetsSpecs;
  }).sort((a, b) => {
    switch (sortBy) {
      case "price-low": return a.price - b.price;
      case "price-high": return b.price - a.price;
      case "rating": return b.rating - a.rating;
      case "name": return a.name.localeCompare(b.name);
      default: return 0;
    }
  }) || [];

  const handleSearch = useCallback(async (searchQuery) => {
    const q = searchQuery || query;
    if (!q.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    setIsLoading(true);
    setSearchResults(null);

    try {
      const response = await axios.post(`${API}/search`, { query: q.trim(), max_results: 50 });
      setSearchResults(response.data);
      addToHistory(q.trim());
      
      // Reset filters to match new results
      if (response.data.results?.length > 0) {
        const prices = response.data.results.map(r => r.price);
        setFilters(prev => ({
          ...prev,
          priceRange: [Math.min(...prices), Math.max(...prices)]
        }));
      }
      
      if (response.data.success) {
        toast.success(`Found ${response.data.results_count} results`);
      } else {
        toast.warning("Search unavailable for this query");
      }
    } catch (error) {
      console.error("Search error:", error);
      toast.error(error.response?.data?.detail || "Search failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [query, addToHistory]);

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
    handleSearch(exampleQuery);
  };

  const handleVoiceResult = (transcript) => {
    setQuery(transcript);
    handleSearch(transcript);
  };

  const handleExportPDF = async () => {
    if (!searchResults || !searchResults.success) return;
    setIsExporting(true);
    toast.info("Generating PDF...");
    try {
      const element = document.getElementById("results-container");
      if (!element) return;
      const canvas = await html2canvas(element, { scale: 2, useCORS: true, logging: false });
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({ orientation: canvas.width > canvas.height ? "landscape" : "portrait", unit: "px", format: [canvas.width, canvas.height] });
      pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
      pdf.save(`${searchResults.query.replace(/\s+/g, "_")}_price_comparison.pdf`);
      toast.success("PDF exported successfully!");
    } catch (error) {
      console.error("PDF export error:", error);
      toast.error("Failed to export PDF");
    } finally {
      setIsExporting(false);
    }
  };

  const resetFilters = () => {
    if (searchResults?.results?.length > 0) {
      const prices = searchResults.results.map(r => r.price);
      setFilters({
        priceRange: [Math.min(...prices), Math.max(...prices)],
        minRating: 0,
        availability: ["In Stock", "Limited Stock", "Pre-Order"],
        sourceTypes: ["Global Suppliers", "Local Markets", "Online Marketplaces"]
      });
    }
  };

  return (
    <div className={`min-h-screen ${isDark ? "dark bg-slate-900" : "bg-white"}`}>
      {/* Hero Section */}
      <AnimatePresence>
        {!searchResults && (
          <motion.section initial={{ opacity: 1 }} exit={{ opacity: 0, height: 0 }} className="hero-gradient dark:bg-slate-900 py-20 md:py-32">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {/* Header Controls */}
              <div className="flex justify-end gap-2 mb-8">
                <FavoritesPanel favorites={favorites} onRemove={removeFavorite} onSearch={handleExampleClick} selectedCurrency={selectedCurrency} />
                <CurrencySwitcher selectedCurrency={selectedCurrency} onCurrencyChange={setSelectedCurrency} />
                <DarkModeToggle isDark={isDark} onToggle={() => setIsDark(!isDark)} />
              </div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="text-center">
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white font-['Manrope'] tracking-tight">
                  Find Any Product,{" "}
                  <span className="gradient-text">Compare Prices Globally</span>
                </h1>
                <p className="mt-6 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                  AI-powered search across global suppliers, local markets, and online marketplaces.
                  Get instant price comparisons and market insights.
                </p>
              </motion.div>

              {/* Search Form */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2, duration: 0.6 }} className="mt-10">
                <div className="search-input-wrapper">
                  <Search className="search-icon w-5 h-5" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                    placeholder="Search for any product... (e.g., laptop, shoes, TV)"
                    disabled={isLoading}
                    className="dark:bg-slate-800 dark:text-white dark:border-slate-700"
                    data-testid="search-input"
                  />
                  <div className="absolute right-16 top-1/2 transform -translate-y-1/2">
                    <VoiceSearchButton onResult={handleVoiceResult} isListening={isListening} setIsListening={setIsListening} />
                  </div>
                  <button onClick={() => handleSearch()} disabled={isLoading} className="submit-btn" data-testid="search-button">
                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  </button>
                </div>

                {/* Example Queries */}
                <div className="example-queries" data-testid="example-queries">
                  {EXAMPLE_QUERIES.map((eq, index) => (
                    <button key={index} onClick={() => handleExampleClick(eq)} className="example-pill dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300" disabled={isLoading} data-testid={`example-query-${index}`}>
                      {eq}
                    </button>
                  ))}
                </div>
              </motion.div>

              {/* Search History */}
              {history.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-8 max-w-xl mx-auto">
                  <SearchHistoryPanel history={history} onSearch={handleExampleClick} onClear={clearHistory} />
                </motion.div>
              )}

              {/* Smart Recommendations */}
              {history.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="mt-6 max-w-xl mx-auto">
                  <SmartRecommendations searchHistory={history} onSearch={handleExampleClick} />
                </motion.div>
              )}

              {/* Feature Cards */}
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5, duration: 0.6 }} className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
                <div className="feature-card dark:bg-slate-800 dark:border-slate-700">
                  <div className="feature-icon blue"><Globe className="w-6 h-6" /></div>
                  <h3 className="feature-title dark:text-white">Universal Search</h3>
                  <p className="feature-description dark:text-slate-400">Search any product across global and local marketplaces worldwide</p>
                </div>
                <div className="feature-card dark:bg-slate-800 dark:border-slate-700">
                  <div className="feature-icon purple"><TrendingUp className="w-6 h-6" /></div>
                  <h3 className="feature-title dark:text-white">AI-Powered Analysis</h3>
                  <p className="feature-description dark:text-slate-400">Smart insights and recommendations powered by advanced AI</p>
                </div>
                <div className="feature-card dark:bg-slate-800 dark:border-slate-700">
                  <div className="feature-icon green"><DollarSign className="w-6 h-6" /></div>
                  <h3 className="feature-title dark:text-white">Best Prices</h3>
                  <p className="feature-description dark:text-slate-400">Compare prices from multiple sources to find the best deals</p>
                </div>
              </motion.div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* Compact Search Bar when results are shown */}
      {searchResults && (
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="sticky top-0 z-50 bg-white/90 dark:bg-slate-900/90 backdrop-blur-lg border-b border-slate-200 dark:border-slate-700 py-4">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4">
              <h1 className="text-xl font-bold text-slate-800 dark:text-white font-['Manrope'] hidden sm:block">
                Price<span className="gradient-text">Nexus</span>
              </h1>
              <div className="flex-1 max-w-xl">
                <div className="search-input-wrapper" style={{ maxWidth: "100%" }}>
                  <Search className="search-icon w-4 h-4" />
                  <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()} placeholder="Search products..." disabled={isLoading} className="dark:bg-slate-800 dark:text-white dark:border-slate-700" style={{ height: "48px", fontSize: "1rem" }} data-testid="search-input-compact" />
                  <button onClick={() => handleSearch()} disabled={isLoading} className="submit-btn" style={{ width: "40px", height: "40px" }} data-testid="search-button-compact">
                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <FavoritesPanel favorites={favorites} onRemove={removeFavorite} onSearch={handleExampleClick} selectedCurrency={selectedCurrency} />
                <CurrencySwitcher selectedCurrency={selectedCurrency} onCurrencyChange={setSelectedCurrency} />
                <DarkModeToggle isDark={isDark} onToggle={() => setIsDark(!isDark)} />
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20" data-testid="loading-state">
          <div className="loading-spinner mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400 animate-pulse-soft">Searching multiple sources...</p>
        </div>
      )}

      {/* Search Results */}
      {searchResults && !isLoading && (
        <div id="results-container" className="results-container dark:bg-slate-900">
          {searchResults.success ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
              {/* Results Header */}
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white font-['Manrope']" data-testid="results-title">
                    Results for "{searchResults.query}"
                  </h2>
                  <p className="text-slate-600 dark:text-slate-400 mt-1">
                    Showing <span className="font-semibold text-blue-600">{filteredResults.length}</span> of {searchResults.results_count} products
                    {" • "}AI Model: <span className="font-mono text-sm">{searchResults.ai_model}</span>
                  </p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <ShareResults query={searchResults.query} resultsCount={filteredResults.length} />
                  <ExportToExcel results={filteredResults} query={searchResults.query} />
                  <Button onClick={handleExportPDF} disabled={isExporting} className="btn-gradient text-white rounded-full px-6" data-testid="export-pdf-button">
                    {isExporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                    Export PDF
                  </Button>
                </div>
              </div>

              {/* Controls Row */}
              <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
                <div className="flex items-center gap-2">
                  <Button variant="outline" onClick={() => setShowFilters(!showFilters)} data-testid="toggle-filters">
                    <Filter className="w-4 h-4 mr-2" />
                    Filters {showFilters ? <ChevronDown className="w-4 h-4 ml-1 rotate-180" /> : <ChevronDown className="w-4 h-4 ml-1" />}
                  </Button>
                  <SortDropdown sortBy={sortBy} onSortChange={setSortBy} />
                </div>
                <ViewToggle view={view} onViewChange={setView} />
              </div>

              {/* Filter Panel */}
              <AnimatePresence>
                {showFilters && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mb-6">
                    <FilterPanel filters={filters} onFiltersChange={setFilters} availableSources={[]} priceRange={priceRange} onReset={resetFilters} />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Price Summary */}
              <div className="mb-8">
                <PriceSummary results={filteredResults} selectedCurrency={selectedCurrency} />
              </div>

              {/* Similar Products */}
              <div className="mb-6">
                <SimilarProducts currentProduct={searchResults.query} onSearch={handleExampleClick} />
              </div>

              {/* Tabs for different views */}
              <Tabs defaultValue="products" className="mb-8">
                <TabsList className="grid w-full grid-cols-6 max-w-2xl dark:bg-slate-800">
                  <TabsTrigger value="products" data-testid="tab-products">Products</TabsTrigger>
                  <TabsTrigger value="vendors" data-testid="tab-vendors">Vendors</TabsTrigger>
                  <TabsTrigger value="charts" data-testid="tab-charts">Charts</TabsTrigger>
                  <TabsTrigger value="distribution" data-testid="tab-distribution">Distribution</TabsTrigger>
                  <TabsTrigger value="insights" data-testid="tab-insights">Insights</TabsTrigger>
                  <TabsTrigger value="sources" data-testid="tab-sources">Sources</TabsTrigger>
                </TabsList>

                <TabsContent value="products" className="mt-6">
                  <div className={view === "grid" ? "product-grid" : "space-y-3"} data-testid="product-grid">
                    {filteredResults.map((product, index) => (
                      <ProductCard 
                        key={index} 
                        product={product} 
                        index={index} 
                        allProducts={filteredResults}
                        view={view}
                        selectedCurrency={selectedCurrency}
                        onFavoriteToggle={isFavorite(product) ? removeFavorite : addFavorite}
                        isFavorite={isFavorite(product)}
                        onCompareToggle={isInCompare(product) ? removeFromCompare : addToCompare}
                        isInCompare={isInCompare(product)}
                      />
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="vendors" className="mt-6">
                  <VendorsSection results={filteredResults} />
                </TabsContent>

                <TabsContent value="charts" className="mt-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <PriceComparisonChart results={filteredResults} selectedCurrency={selectedCurrency} />
                    <SourceDistributionChart results={filteredResults} />
                  </div>
                </TabsContent>

                <TabsContent value="distribution" className="mt-6">
                  <PriceDistributionChart results={filteredResults} />
                </TabsContent>

                <TabsContent value="insights" className="mt-6">
                  <Card className="dark:bg-slate-800 dark:border-slate-700">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 font-['Manrope'] dark:text-white">
                        <TrendingUp className="w-5 h-5 text-blue-600" />
                        Market Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <MarkdownContent content={searchResults.response} />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="sources" className="mt-6">
                  <DataSourcesSection dataSources={searchResults.data_sources} />
                </TabsContent>
              </Tabs>
            </motion.div>
          ) : (
            <SearchUnavailable query={searchResults.query} />
          )}
        </div>
      )}

      {/* Compare Modal */}
      <CompareModal compareList={compareList} onRemove={removeFromCompare} onClear={clearCompare} selectedCurrency={selectedCurrency} />

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-600 dark:text-slate-400">
            <span className="font-semibold font-['Manrope']">Price<span className="gradient-text">Nexus</span></span>
            {" "}• AI-Powered Global Price Comparison
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-500 mt-2">
            Search results are generated for demonstration purposes
          </p>
        </div>
      </footer>

      <Toaster position="top-right" richColors theme={isDark ? "dark" : "light"} />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<SearchPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
