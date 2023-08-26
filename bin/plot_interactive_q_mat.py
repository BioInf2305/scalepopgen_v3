from os import popen
import sys
import argparse
import pandas as pd
import yaml
from yaml.loader import SafeLoader
import math
from bokeh.plotting import figure, show
from bokeh.models import HoverTool, ColumnDataSource, Legend
from bokeh.plotting import show, figure
from bokeh.plotting import figure, save, output_file
from bokeh.models.tickers import FixedTicker


class PlotAdmixture:
    def __init__(self, q_file, fam_f, yml_file, col_sp_f, outprefix, pop_order):
        self.outprefix = outprefix  # prefix of the output file
        self.q_file = q_file  # q matrix generated by admixture tool
        self.fam_f = fam_f  # .fam file correspoding to input used to generated q matrix
        self.yml_file = yml_file  # yml file containing parameters for the figure
        self.col_sp_f = col_sp_f  # file containining first column as color codes and (optional) second column as hatch pattern of bokeh
        self.pop_order = pop_order  # the orders in which the population bar plots should be arranged.
        self.legend_loc_list = [[]]  # legend loc list --> internal use
        self.axis_sample_dict = (
            {}
        )  # dictionary with x axis coordinates as key and sample id as value
        self.axis_pop_dict = (
            {}
        )  # dictionary with x axis cordinates as key ans population id  as value

    def prepare_q_file_dict(self):
        """
        method prepare a dictionary with line count as key and corresponding K-values as its values
        """
        lc = 0
        cnt_q_dict = {}
        with open(self.q_file) as source:
            for line in source:
                lc += 1
                q_float_list = list(map(float, line.rstrip().split()))
                q_acc_list = []
                for i in range(len(q_float_list)):
                    if i == 0:
                        q_acc_list.append(q_float_list[i])
                    else:
                        q_acc_list.append(q_acc_list[-1] + q_float_list[i])
                cnt_q_dict[lc] = q_acc_list[:]
        return cnt_q_dict

    def prepare_pop_sample_dict(self):
        """
        this method outputs three dictionaries:
            --> line count as key and corresponding population as its value
            --> line count as key and corresponding sample as its value
            --> pop id as key and corresponding sample as its value
        """
        lc = 0
        lc_sample_d = {}
        pop_sample_d = {}
        lc_pop_d = {}
        n1_pop_sample_d = {}
        with open(self.fam_f) as source:
            for line in source:
                line = line.rstrip().split()
                lc += 1
                lc_pop_d[lc] = line[0]
                lc_sample_d[lc] = line[1]
                if line[0] not in lc_sample_d:
                    pop_sample_d[line[0]] = []
                pop_sample_d[line[0]].append(line[1])
        if self.pop_order != "none":
            with open(self.pop_order) as source:
                for line in source:
                    line = line.rstrip().split()
                    n1_pop_sample_d[line[0]] = pop_sample_d[line[0]]
        else:
            for pop in pop_sample_d:
                n1_pop_sample_d[pop] = pop_sample_d[pop]
        return lc_pop_d, lc_sample_d, n1_pop_sample_d

    def prepare_col_sp_f_l(self):
        """
        read the map file with the first column as color id and if second column is present--> hatch pattern
        """
        pop_sp_col_l = []
        with open(self.col_sp_f) as source:
            for line in source:
                line = line.rstrip().split()
                self.is_hatch_pattern = True if len(line) == 2 else False
                pop_sp_col_l.append([line[0], line[1]]) if len(
                    line
                ) == 2 else pop_sp_col_l.append(line[0])
        return pop_sp_col_l

    def read_yml_file(self):
        """
        read yml file and set the parameters corresponding to the interactive plot
        """
        with open(self.yml_file, "r") as p:
            params = yaml.load(p, Loader=SafeLoader)
        self.figure_width = params["width"]
        self.figure_height = params["height"]
        self.bar_width = params["bar_width"]
        self.sample_label_orientation = params["sample_label_orientation"]
        self.pop_label_orientation = params["pop_label_orientation"]
        self.space_pop_group = params["space_pop_group"]
        self.legend_font_size = params["legend_font_size"]
        self.label_font_size = params["label_font_size"]
        self.fil_alpha = params["fil_alpha"]
        self.num_legend_per_col = params["num_legend_per_col"]

    def add_plot(self, lst_df, i):
        """
        plot the data and collect the list of legends and correspondign figure object
        """
        pd1 = (
            pd.DataFrame(
                lst_df, columns=["sn", "pn", "anc_1", "anc_2", "sc", "col", "idx"]
            )
            if self.is_hatch_pattern
            else pd.DataFrame(
                lst_df, columns=["sn", "pn", "anc_1", "anc_2", "col", "idx"]
            )
        )
        source = ColumnDataSource(pd1)
        s = (
            self.p.vbar(
                x="idx",
                bottom="anc_1",
                top="anc_2",
                width=self.bar_width,
                color="col",
                fill_alpha=self.fil_alpha,
                hatch_pattern="sc",
                source=source,
            )
            if self.is_hatch_pattern
            else self.p.vbar(
                x="idx",
                bottom="anc_1",
                top="anc_2",
                width=self.bar_width,
                color="col",
                fill_alpha=self.fil_alpha,
                source=source,
            )
        )
        if i == 0:
            self.p.add_tools(HoverTool(tooltips=[("sample", "@sn"), ("pop", "@pn")]))
        if len(self.legend_loc_list[-1]) <= self.num_legend_per_col:
            self.legend_loc_list[-1].append(("k=" + str(i), [s]))
        else:
            self.legend_loc_list.append([])
            self.legend_loc_list[-1].append(("k=" + str(i), [s]))

    def format_plot(self):
        """
        format the plot using the parameters set in yml file
        """
        shift = 0
        for l_loc in self.legend_loc_list:
            shift += 3
            legend = Legend(items=l_loc, location=(0 - shift, -30 - shift))
            self.p.add_layout(legend, "right")
        self.p.xaxis.major_label_text_font_size = self.label_font_size
        self.p.legend.label_text_font_size = self.legend_font_size
        self.p.xaxis.ticker = FixedTicker(ticks=list(self.axis_pop_dict.values()))
        self.p.xaxis.major_label_overrides = {
            v: k for k, v in self.axis_pop_dict.items()
        }
        self.p.xaxis.major_tick_out = 15
        self.p.xaxis.major_label_orientation = math.radians(self.pop_label_orientation)
        self.p.legend.click_policy = "hide"
        self.p.grid.visible = False

    def main_func(self):
        self.read_yml_file()
        self.p = figure(width=self.figure_width, height=self.figure_height)
        self.p.output_backend = "svg"
        output_file(self.outprefix + ".html")
        pop_sp_col_l = self.prepare_col_sp_f_l()
        cnt_q_dict = self.prepare_q_file_dict()
        lc_pop_d, lc_sample_d, pop_sample_d = self.prepare_pop_sample_dict()
        anc_cnt = len(cnt_q_dict[list(cnt_q_dict.keys())[0]])
        for i in range(anc_cnt):
            pos = self.bar_width
            lct_dict = {}
            for lct in cnt_q_dict:
                lct_tmp_l = []
                pop = lc_pop_d[lct]
                if pop not in lct_dict:
                    lct_dict[pop] = []
                lct_tmp_l.append(lc_sample_d[lct])
                lct_tmp_l.append(pop)
                if i == 0:
                    lct_tmp_l.append(0)
                else:
                    lct_tmp_l.append(cnt_q_dict[lct][i - 1])
                lct_tmp_l.append(cnt_q_dict[lct][i])
                lct_dict[pop].append(lct_tmp_l[:])
            lst_df = []
            for pop in pop_sample_d:
                pos += self.space_pop_group
                for lst in lct_dict[pop]:
                    pos += self.bar_width
                    self.axis_sample_dict[lst[0]] = pos
                    if self.is_hatch_pattern:
                        lst.append(pop_sp_col_l[i][1])
                        lst.append(pop_sp_col_l[i][0])
                    else:
                        lst.append(pop_sp_col_l[i])
                    lst.append(pos)
                    lst_df.append(lst[:])
                self.axis_pop_dict[pop] = pos
            self.add_plot(lst_df, i)
        self.format_plot()
        save(self.p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A small python script to plot q-matrix generated by ADMIXRTURE program interactively",
        epilog="author: Maulik upadhyay (upadhyay.maulik@gmail.com)",
    )
    parser.add_argument(
        "-q",
        "--q_file",
        metavar="String",
        help="q matrix generated by admixture tool",
        required=True,
    )
    parser.add_argument(
        "-f",
        "--fam_file",
        metavar="String",
        help=".fam file corresponding to .bim file which was supplied as input to generate the q matrix",
        required=True,
    )
    parser.add_argument(
        "-y",
        "--yml_file",
        metavar="String",
        help="yaml file containing parameters of plots to be generated",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--col_file",
        metavar="String",
        help="file containing hex color codes for each value of K, note that this file can have one or two columns. First col --> hex color codes, second col--> hatch pattern supported by bokeh. The second column is optional",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--outprefix",
        metavar="String",
        help="the output prefix of html file",
        required=True,
    )
    parser.add_argument(
        "-s",
        "--sort_pop",
        metavar="String",
        help="the file containing the population ids in order in which it is to be displayed on the plot",
        default="none",
        required=False,
    )
    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        plot_ad = PlotAdmixture(
            args.q_file,
            args.fam_file,
            args.yml_file,
            args.col_file,
            args.outprefix,
            args.sort_pop,
        )
        plot_ad.main_func()